import json
import asyncio
from typing import Dict, List
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import Player, GameInvitation, Battle
from .battle_engine import BattleMatchmaker


class GlobalNotificationsConsumer(AsyncWebsocketConsumer):
    """Global WebSocket consumer dla powiadomień (zaproszenia do gry, wiadomości, etc.)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.player = None
        self.user_group_name = None
    
    async def connect(self):
        """Połączenie do globalnego kanału powiadomień"""
        # Sprawdź autoryzację
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Pobierz gracza
        try:
            self.player = await database_sync_to_async(Player.objects.get)(user=self.user)
        except Player.DoesNotExist:
            await self.close()
            return
        
        # Dołącz do grupy użytkownika
        self.user_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notifications',
            'user_id': self.user.id,
            'username': self.user.username
        }))
        
        # Wyślij pending invitations przy połączeniu
        await self.send_pending_invitations()
    
    async def disconnect(self, close_code):
        """Rozłączenie z globalnego kanału"""
        if self.user_group_name:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Obsługa wiadomości od klienta"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'send_game_invitation':
                await self.send_game_invitation(data)
            elif message_type == 'respond_to_invitation':
                await self.respond_to_invitation(data)
            elif message_type == 'cancel_invitation':
                await self.cancel_invitation(data)
            elif message_type == 'get_pending_invitations':
                await self.send_pending_invitations()
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            await self.send_error(f"Error processing message: {str(e)}")
    
    async def send_game_invitation(self, data):
        """Wysyła zaproszenie do gry"""
        try:
            receiver_username = data.get('receiver_username')
            invitation_type = data.get('invitation_type', 'friendly')
            sender_creatures = data.get('sender_creatures', [])
            
            if not receiver_username:
                await self.send_error("Receiver username required")
                return
            
            if not sender_creatures:
                await self.send_error("Sender creatures required")
                return
            
            # Sprawdź czy receiver istnieje
            try:
                receiver_user = await database_sync_to_async(
                    lambda: self.user.__class__.objects.get(username=receiver_username)
                )()
                receiver_player = await database_sync_to_async(
                    Player.objects.get
                )(user=receiver_user)
            except:
                await self.send_error("Receiver not found")
                return
            
            # Sprawdź czy nie wysyłamy zaproszenia sami sobie
            if receiver_user.id == self.user.id:
                await self.send_error("Cannot invite yourself")
                return
            
            # Sprawdź czy nie ma już pending invitation między tymi graczami
            existing_invitation = await database_sync_to_async(
                lambda: GameInvitation.objects.filter(
                    sender=self.player,
                    receiver=receiver_player,
                    status='pending'
                ).first()
            )()
            
            if existing_invitation and not existing_invitation.is_expired():
                await self.send_error("Invitation already pending")
                return
            
            # Waliduj creatures
            valid_creatures = await self.validate_player_creatures(sender_creatures)
            if not valid_creatures:
                await self.send_error("Invalid creatures selected")
                return
            
            # Utwórz zaproszenie
            invitation = await database_sync_to_async(GameInvitation.objects.create)(
                sender=self.player,
                receiver=receiver_player,
                invitation_type=invitation_type,
                sender_creatures=sender_creatures
            )
            
            # Wyślij powiadomienie do receiver
            receiver_group = f"user_{receiver_user.id}"
            await self.channel_layer.group_send(receiver_group, {
                'type': 'game_invitation_received',
                'invitation_id': str(invitation.id),
                'sender_username': self.user.username,
                'invitation_type': invitation_type,
                'expires_at': invitation.expires_at.isoformat(),
                'sender_creatures_count': len(sender_creatures)
            })
            
            # Potwierdź wysłanie sender-owi
            await self.send(text_data=json.dumps({
                'type': 'invitation_sent',
                'invitation_id': str(invitation.id),
                'receiver_username': receiver_username,
                'message': f'Invitation sent to {receiver_username}'
            }))
            
        except Exception as e:
            await self.send_error(f"Error sending invitation: {str(e)}")
    
    async def respond_to_invitation(self, data):
        """Odpowiada na zaproszenie do gry"""
        try:
            invitation_id = data.get('invitation_id')
            response = data.get('response')  # 'accepted' lub 'declined'
            receiver_creatures = data.get('receiver_creatures', [])
            
            if not invitation_id or response not in ['accepted', 'declined']:
                await self.send_error("Invalid response data")
                return
            
            # Pobierz zaproszenie
            try:
                invitation = await database_sync_to_async(
                    GameInvitation.objects.get
                )(id=invitation_id, receiver=self.player)
            except GameInvitation.DoesNotExist:
                await self.send_error("Invitation not found")
                return
            
            if not invitation.can_respond():
                await self.send_error("Invitation expired or already responded")
                return
            
            # Zaktualizuj status zaproszenia
            invitation.status = response
            invitation.responded_at = timezone.now()
            await database_sync_to_async(invitation.save)()
            
            # Wyślij odpowiedź do sender
            sender_group = f"user_{invitation.sender.user.id}"
            
            if response == 'accepted':
                # Waliduj creatures receiver-a
                if receiver_creatures:
                    valid_creatures = await self.validate_player_creatures(receiver_creatures)
                    if not valid_creatures:
                        await self.send_error("Invalid creatures selected")
                        return
                
                # Utwórz walkę
                battle = await database_sync_to_async(BattleMatchmaker.create_battle)(
                    invitation.sender, invitation.invitation_type
                )
                
                # Dołącz graczy do walki
                success = await database_sync_to_async(BattleMatchmaker.join_battle)(
                    battle, invitation.receiver, invitation.sender_creatures, receiver_creatures
                )
                
                if success:
                    # Powiąż zaproszenie z walką
                    invitation.battle = battle
                    await database_sync_to_async(invitation.save)()
                    
                    # Powiadom obu graczy o rozpoczęciu walki
                    battle_data = await self.get_battle_start_data(battle)
                    
                    await self.channel_layer.group_send(sender_group, {
                        'type': 'invitation_accepted',
                        'invitation_id': str(invitation.id),
                        'receiver_username': self.user.username,
                        'battle_id': str(battle.id),
                        'battle_data': battle_data
                    })
                    
                    await self.send(text_data=json.dumps({
                        'type': 'invitation_accepted',
                        'invitation_id': str(invitation.id),
                        'battle_id': str(battle.id),
                        'battle_data': battle_data
                    }))
                else:
                    await self.send_error("Failed to create battle")
            else:
                # Zaproszenie odrzucone
                await self.channel_layer.group_send(sender_group, {
                    'type': 'invitation_declined',
                    'invitation_id': str(invitation.id),
                    'receiver_username': self.user.username
                })
                
                await self.send(text_data=json.dumps({
                    'type': 'invitation_declined',
                    'invitation_id': str(invitation.id)
                }))
            
        except Exception as e:
            await self.send_error(f"Error responding to invitation: {str(e)}")
    
    async def cancel_invitation(self, data):
        """Anuluje wysłane zaproszenie"""
        try:
            invitation_id = data.get('invitation_id')
            
            if not invitation_id:
                await self.send_error("Invitation ID required")
                return
            
            # Pobierz zaproszenie (tylko sender może anulować)
            try:
                invitation = await database_sync_to_async(
                    GameInvitation.objects.get
                )(id=invitation_id, sender=self.player, status='pending')
            except GameInvitation.DoesNotExist:
                await self.send_error("Invitation not found or cannot be cancelled")
                return
            
            # Anuluj zaproszenie
            invitation.status = 'cancelled'
            await database_sync_to_async(invitation.save)()
            
            # Powiadom receiver o anulowaniu
            receiver_group = f"user_{invitation.receiver.user.id}"
            await self.channel_layer.group_send(receiver_group, {
                'type': 'invitation_cancelled',
                'invitation_id': str(invitation.id),
                'sender_username': self.user.username
            })
            
            await self.send(text_data=json.dumps({
                'type': 'invitation_cancelled',
                'invitation_id': str(invitation.id)
            }))
            
        except Exception as e:
            await self.send_error(f"Error cancelling invitation: {str(e)}")
    
    async def send_pending_invitations(self):
        """Wysyła listę oczekujących zaproszeń"""
        try:
            # Received invitations
            received_invitations = await database_sync_to_async(lambda: list(
                GameInvitation.objects.filter(
                    receiver=self.player,
                    status='pending'
                ).select_related('sender__user')
            ))()
            
            # Sent invitations
            sent_invitations = await database_sync_to_async(lambda: list(
                GameInvitation.objects.filter(
                    sender=self.player,
                    status='pending'
                ).select_related('receiver__user')
            ))()
            
            # Filtruj wygasłe zaproszenia
            valid_received = [inv for inv in received_invitations if not inv.is_expired()]
            valid_sent = [inv for inv in sent_invitations if not inv.is_expired()]
            
            received_data = []
            for inv in valid_received:
                received_data.append({
                    'invitation_id': str(inv.id),
                    'sender_username': inv.sender.user.username,
                    'invitation_type': inv.invitation_type,
                    'expires_at': inv.expires_at.isoformat(),
                    'sender_creatures_count': len(inv.sender_creatures)
                })
            
            sent_data = []
            for inv in valid_sent:
                sent_data.append({
                    'invitation_id': str(inv.id),
                    'receiver_username': inv.receiver.user.username,
                    'invitation_type': inv.invitation_type,
                    'expires_at': inv.expires_at.isoformat()
                })
            
            await self.send(text_data=json.dumps({
                'type': 'pending_invitations',
                'received_invitations': received_data,
                'sent_invitations': sent_data
            }))
            
        except Exception as e:
            await self.send_error(f"Error getting pending invitations: {str(e)}")
    
    # Event handlers dla group_send
    async def game_invitation_received(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def invitation_accepted(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def invitation_declined(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def invitation_cancelled(self, event):
        await self.send(text_data=json.dumps(event))
    
    # Helper methods
    async def send_error(self, message: str):
        """Wysyła błąd do klienta"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    async def validate_player_creatures(self, creature_ids: List[int]) -> bool:
        """Sprawdza czy gracz posiada podane creatures"""
        try:
            count = await database_sync_to_async(
                self.player.creatures.filter(id__in=creature_ids).count
            )()
            return count == len(creature_ids)
        except:
            return False
    
    async def get_battle_start_data(self, battle):
        """Pobiera dane do rozpoczęcia walki"""
        participants = await database_sync_to_async(lambda: list(
            battle.participants.all().select_related('creature', 'player__user')
        ))()
        
        participants_data = []
        for p in participants:
            participants_data.append({
                'creature_id': p.creature.id,
                'name': p.creature.name,
                'max_hp': p.creature.max_hp,
                'current_hp': p.current_hp,
                'initiative': p.creature.initiative,
                'team': p.team,
                'player_name': p.player.user.username
            })
        
        return {
            'battle_id': str(battle.id),
            'battle_type': battle.battle_type,
            'participants': participants_data
        }