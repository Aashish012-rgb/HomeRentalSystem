from django.urls import path

from .consumers import BookingChatConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:booking_id>/", BookingChatConsumer.as_asgi()),
]
