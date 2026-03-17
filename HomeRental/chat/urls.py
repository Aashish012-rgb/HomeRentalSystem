"""
Chat App URL Configuration
REST API endpoints for chat operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]

"""
API Endpoints Documentation:

CHAT ENDPOINTS:
================

1. List all chats for current user:
   GET /api/chat/chats/
   Returns: List of chats with last message and unread count

2. Get specific chat with all messages:
   GET /api/chat/chats/{id}/
   Returns: Chat details with all messages and participants

3. Create or get chat for a booking:
   POST /api/chat/chats/create_or_get/
   Data: {"booking_id": <int>}
   Returns: Chat object (only if booking is accepted)

4. Mark messages as read in a chat:
   POST /api/chat/chats/{id}/mark_as_read/
   Returns: Confirmation message

5. Get paginated messages for a chat:
   GET /api/chat/chats/{id}/messages/
   Query params: page=1, page_size=20
   Returns: Paginated list of messages

MESSAGE ENDPOINTS:
==================

1. Send a message:
   POST /api/chat/messages/
   Data: {"chat": <chat_id>, "content": "<message_content>"}
   Returns: Created message object

2. Get message by chat:
   GET /api/chat/messages/by_chat/?chat_id=<int>
   Returns: Paginated messages for the chat

3. Delete a message (only by sender):
   DELETE /api/chat/messages/{id}/
   Returns: 204 No Content

WEBSOCKET ENDPOINTS:
====================

1. Chat WebSocket connection:
   ws://localhost:8000/ws/chat/<chat_id>/
   
   Sending messages:
   {
       "type": "chat_message",
       "message": "Your message content"
   }
   
   Mark as read:
   {
       "type": "mark_as_read",
       "message_ids": [1, 2, 3]
   }
   
   Receiving messages:
   {
       "type": "chat_message",
       "id": <message_id>,
       "sender_id": <user_id>,
       "sender_username": "username",
       "content": "message content",
       "timestamp": "2024-03-17T12:30:45.123456Z",
       "is_read": false
   }
   
   User status updates:
   {
       "type": "user_status",
       "status": "online|offline",
       "user_id": <user_id>,
       "username": "username"
   }
"""
