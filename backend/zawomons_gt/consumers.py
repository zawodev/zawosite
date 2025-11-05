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
        self.guest_username = None  # Will be set from first message
        self.player_removed = False  # Flag to track if player was already removed

        print(f'🔌 WebSocket connecting to lobby: {self.lobby_code}')
        print(f'👤 User: {self.user}')

        # Join lobby group
        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name
        )

        await self.accept()
        print(f'✅ WebSocket accepted for lobby: {self.lobby_code}')

        # Send current lobby state
        lobby_data = await self.get_lobby_data()
        print(f'📊 Lobby data: {lobby_data}')
        if lobby_data:
            await self.send(text_data=json.dumps({
                'type': 'lobby_state',
                'lobby': lobby_data
            }))
            print(f'📤 Sent lobby_state to client')
        else:
            print(f'⚠️ No lobby data found for code: {self.lobby_code}')

    async def disconnect(self, close_code):
        print(f'🔌 WebSocket disconnected from lobby: {self.lobby_code} (close_code: {close_code})')
        
        # Only remove player if not already removed (e.g., by leave button)
        if not self.player_removed:
            await self.remove_player_and_cleanup()
        else:
            print(f'⏭️ Player already removed via REST API, skipping cleanup')
        
        # Leave lobby group
        await self.channel_layer.group_discard(
            self.lobby_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Store guest_username from any message that contains it
        if not self.guest_username and data.get('guest_username'):
            self.guest_username = data.get('guest_username')
            print(f'👤 Guest username identified: {self.guest_username}')

        if message_type == 'identify':
            # Just identification message, already processed above
            pass
        elif message_type == 'player_ready':
            await self.handle_player_ready(data)
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

    async def lobby_closed(self, event):
        """Handle lobby closure notification"""
        await self.send(text_data=json.dumps({
            'type': 'lobby_closed',
            'reason': event.get('reason', 'Lobby was closed')
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
    def remove_player_and_cleanup(self):
        """Remove player from lobby and delete lobby if empty or if creator left"""
        try:
            lobby = Lobby.objects.get(code=self.lobby_code)
            player = None
            
            # Try to find the player to remove
            if self.user and self.user.is_authenticated:
                player = LobbyPlayer.objects.filter(lobby=lobby, user=self.user).first()
                if player:
                    print(f'🔍 Found authenticated player: {player.display_name}')
            elif self.guest_username:
                player = LobbyPlayer.objects.filter(lobby=lobby, guest_username=self.guest_username).first()
                if player:
                    print(f'🔍 Found guest player by username: {player.display_name}')
            
            # If player not found, they were already removed (e.g., by leave button)
            # In this case, DON'T delete the lobby - other players are still there
            if not player:
                print(f'⚠️ Player not found in lobby {self.lobby_code} (already removed via REST API)')
                print(f'📊 Lobby currently has {lobby.players.count()} players remaining')
                print(f'✅ Keeping lobby {self.lobby_code} with existing players')
                
                # Only delete if lobby is truly empty (all players gone)
                if lobby.players.count() == 0:
                    print(f'🧹 Deleting empty lobby: {self.lobby_code}')
                    lobby.delete()
                return
            
            # Check if this is the creator (first player)
            first_player = lobby.players.order_by('id').first()
            is_creator = first_player and first_player.id == player.id
            
            # Remove the player
            player_display_name = player.display_name
            player.delete()
            print(f'🚪 Player {player_display_name} removed from lobby {self.lobby_code}')
            
            # Refresh lobby from database to get accurate count
            lobby.refresh_from_db()
            remaining_players = lobby.players.count()
            
            # Check if lobby is now empty OR if creator left
            if remaining_players == 0 or is_creator:
                print(f'🧹 Deleting lobby {self.lobby_code} ({"empty" if remaining_players == 0 else "creator left"})')
                
                # If creator left, notify remaining players before deleting
                if is_creator and remaining_players > 0:
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'lobby_{self.lobby_code}',
                        {
                            'type': 'lobby_closed',
                            'reason': 'Host left the lobby'
                        }
                    )
                
                lobby.delete()
            else:
                print(f'👥 Lobby {self.lobby_code} still has {remaining_players} players')
                # Notify remaining players about the update
                from channels.layers import get_channel_layer
                from .serializers import LobbySerializer
                channel_layer = get_channel_layer()
                from asgiref.sync import async_to_sync
                async_to_sync(channel_layer.group_send)(
                    f'lobby_{self.lobby_code}',
                    {
                        'type': 'lobby_update',
                        'lobby': LobbySerializer(lobby).data
                    }
                )
                
        except Lobby.DoesNotExist:
            print(f'⚠️ Lobby {self.lobby_code} already deleted')
            pass
