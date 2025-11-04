import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Lobby, LobbyPlayer
from .serializers import LobbySerializer

User = get_user_model()


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_code = self.scope['url_route']['kwargs']['lobby_code']
        self.lobby_group_name = f'lobby_{self.lobby_code}'
        self.user = self.scope.get('user')

        # Join lobby group
        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name
        )

        await self.accept()

        # Send current lobby state
        lobby_data = await self.get_lobby_data()
        if lobby_data:
            await self.send(text_data=json.dumps({
                'type': 'lobby_state',
                'lobby': lobby_data
            }))

    async def disconnect(self, close_code):
        # Leave lobby group
        await self.channel_layer.group_discard(
            self.lobby_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'player_ready':
            await self.handle_player_ready(data)
        elif message_type == 'settings_update':
            await self.handle_settings_update(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)

    async def handle_player_ready(self, data):
        is_ready = data.get('is_ready', False)
        guest_username = data.get('guest_username', None)
        
        success = await self.update_player_ready(is_ready, guest_username)
        
        if success:
            lobby_data = await self.get_lobby_data()
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'lobby_update',
                    'lobby': lobby_data
                }
            )

    async def handle_settings_update(self, data):
        settings = data.get('settings', {})
        success = await self.update_lobby_settings(settings)
        
        if success:
            lobby_data = await self.get_lobby_data()
            await self.channel_layer.group_send(
                self.lobby_group_name,
                {
                    'type': 'lobby_update',
                    'lobby': lobby_data
                }
            )

    async def handle_chat_message(self, data):
        message = data.get('message', '')
        username = data.get('username', 'Guest')
        
        await self.channel_layer.group_send(
            self.lobby_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def lobby_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'lobby_state',
            'lobby': event['lobby']
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username']
        }))

    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player': event['player']
        }))

    async def player_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'player_id': event['player_id']
        }))

    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'lobby': event['lobby']
        }))

    @database_sync_to_async
    def get_lobby_data(self):
        try:
            lobby = Lobby.objects.get(code=self.lobby_code)
            return LobbySerializer(lobby).data
        except Lobby.DoesNotExist:
            return None

    @database_sync_to_async
    def update_player_ready(self, is_ready, guest_username):
        try:
            lobby = Lobby.objects.get(code=self.lobby_code)
            
            if self.user and self.user.is_authenticated:
                player = LobbyPlayer.objects.get(lobby=lobby, user=self.user)
            else:
                player = LobbyPlayer.objects.get(lobby=lobby, guest_username=guest_username)
            
            player.is_ready = is_ready
            player.save()
            return True
        except (Lobby.DoesNotExist, LobbyPlayer.DoesNotExist):
            return False

    @database_sync_to_async
    def update_lobby_settings(self, settings):
        try:
            lobby = Lobby.objects.get(code=self.lobby_code)
            
            # Only host can update
            if not self.user or lobby.host != self.user:
                return False
            
            for key, value in settings.items():
                if hasattr(lobby, key):
                    setattr(lobby, key, value)
            
            lobby.save()
            return True
        except Lobby.DoesNotExist:
            return False
