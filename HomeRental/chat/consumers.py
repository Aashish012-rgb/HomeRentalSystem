"""
Django Channels Consumer for Real-Time Chat
Handles WebSocket connections and real-time message updates.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer for real-time chat messaging.
    
    Handles:
    - Connection to chat room
    - Sending and receiving messages
    - Broadcasting messages to all participants
    - Marking messages as read
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        
        # Verify user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user is participant in chat
        is_participant = await self.check_chat_access()
        if not is_participant:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify other users that someone joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'status': 'online',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            # Notify other users that someone left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'status': 'offline',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
        except Exception as e:
            logger.warning(f"Could not send offline status for user {self.user.id} in chat {self.chat_id}: {e}")
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
            return
        
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'mark_as_read':
            await self.handle_mark_as_read(data)
        else:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Unknown message type'
            }))
    
    async def handle_chat_message(self, data):
        """Handle incoming chat message"""
        content = data.get('message', '').strip()
        
        if not content:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return
        
        # Verify chat access again
        is_participant = await self.check_chat_access()
        if not is_participant:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Permission denied'
            }))
            return
        
        # Create message in database
        message = await self.save_message(content)
        
        if message:
            # Broadcast message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': message.id,
                    'sender_id': message.sender.id,
                    'sender_username': message.sender.username,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'is_read': message.is_read
                }
            )
    
    async def handle_mark_as_read(self, data):
        """Handle mark messages as read"""
        message_ids = data.get('message_ids', [])
        
        if not message_ids:
            return
        
        await self.mark_messages_as_read(message_ids)
    
    # Channel layer message handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(json.dumps({
            'type': 'chat_message',
            'id': event['id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))
    
    async def user_status(self, event):
        """Send user status update to WebSocket"""
        # Don't send own status back to self
        if event['user_id'] != self.user.id:
            await self.send(json.dumps({
                'type': 'user_status',
                'status': event['status'],
                'user_id': event['user_id'],
                'username': event['username']
            }))
    
    # Database operations
    @database_sync_to_async
    def check_chat_access(self):
        """Check if user has access to this chat"""
        from .models import Chat
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return chat.participants.filter(id=self.user.id).exists()
        except Chat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database"""
        from .models import Chat, Message
        try:
            chat = Chat.objects.get(id=self.chat_id)
            message = Message.objects.create(
                chat=chat,
                sender=self.user,
                content=content
            )
            return message
        except Chat.DoesNotExist:
            return None
    
    @database_sync_to_async
    def mark_messages_as_read(self, message_ids):
        """Mark messages as read"""
        from .models import Chat
        try:
            chat = Chat.objects.get(id=self.chat_id)
            if chat.participants.filter(id=self.user.id).exists():
                chat.messages.filter(
                    id__in=message_ids,
                    is_read=False
                ).exclude(sender=self.user).update(is_read=True)
        except Chat.DoesNotExist:
            pass
