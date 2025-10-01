# Simple WebSocket consumer for invitations only
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class SimpleInvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get user from token (simplified)
        self.user = None
        
        # Accept connection
        await self.accept()
        
        # Add to personal group
        if self.user:
            self.group_name = f"user_{self.user.username}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Remove from group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'send_invitation':
                await self.handle_send_invitation(data)
            elif message_type == 'accept_invitation':
                await self.handle_accept_invitation(data)
            elif message_type == 'decline_invitation':
                await self.handle_decline_invitation(data)
                
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))

    async def handle_send_invitation(self, data):
        target_username = data.get('data', {}).get('target_username')
        from_username = data.get('from_username')
        
        if not target_username or not from_username:
            return
        
        # Send invitation to target user
        target_group = f"user_{target_username}"
        await self.channel_layer.group_send(
            target_group,
            {
                'type': 'invitation_message',
                'message_type': 'invitation_received',
                'from_username': from_username
            }
        )
        
        logger.info(f"Invitation sent from {from_username} to {target_username}")

    async def handle_accept_invitation(self, data):
        from_username = data.get('data', {}).get('from_username')
        accepter_username = data.get('from_username')
        
        if not from_username or not accepter_username:
            return
        
        # Send acceptance back to inviter
        inviter_group = f"user_{from_username}"
        await self.channel_layer.group_send(
            inviter_group,
            {
                'type': 'invitation_message',
                'message_type': 'invitation_accepted',
                'from_username': accepter_username
            }
        )
        
        logger.info(f"Invitation accepted by {accepter_username} for {from_username}")

    async def handle_decline_invitation(self, data):
        from_username = data.get('data', {}).get('from_username')
        decliner_username = data.get('from_username')
        
        if not from_username or not decliner_username:
            return
        
        # Send decline back to inviter
        inviter_group = f"user_{from_username}"
        await self.channel_layer.group_send(
            inviter_group,
            {
                'type': 'invitation_message',
                'message_type': 'invitation_declined',
                'from_username': decliner_username
            }
        )
        
        logger.info(f"Invitation declined by {decliner_username} for {from_username}")

    # Handler for group messages
    async def invitation_message(self, event):
        await self.send(text_data=json.dumps({
            'type': event['message_type'],
            'from_username': event['from_username']
        }))