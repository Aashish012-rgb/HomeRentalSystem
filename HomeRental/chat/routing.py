"""
Django Channels Routing Configuration
Defines WebSocket URL patterns for chat messaging.
"""

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        'ws/chat/<int:chat_id>/',
        consumers.ChatConsumer.as_asgi(),
        name='ws_chat'
    ),
]
