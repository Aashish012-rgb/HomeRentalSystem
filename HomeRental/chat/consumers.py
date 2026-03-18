import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .services import (
    create_chat_message_for_user,
    get_chat_booking_for_user_id,
    room_name_for_booking,
)


class BookingChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.booking_id = int(self.scope["url_route"]["kwargs"]["booking_id"])
        self.room_group_name = room_name_for_booking(self.booking_id)

        if not getattr(self.user, "is_authenticated", False):
            await self.close(code=4401)
            return

        has_access = await self.user_has_chat_access()
        if not has_access:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data is not None:
            await self.send_error("Binary messages are not supported.")
            return

        if text_data is None:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("Invalid chat payload.")
            return

        if payload.get("type") not in (None, "chat.message"):
            await self.send_error("Unsupported chat event.")
            return

        content = (payload.get("message") or "").strip()
        if not content:
            await self.send_error("Message cannot be empty.")
            return

        if len(content) > 1000:
            await self.send_error("Message must be 1000 characters or fewer.")
            return

        message = await database_sync_to_async(create_chat_message_for_user)(
            booking_id=self.booking_id,
            user_id=self.user.id,
            content=content,
        )
        if not message:
            await self.send_error(
                "Chat is only available to the tenant and owner while the booking is accepted."
            )
            await self.close(code=4403)
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat.message",
                    "message": event["message"],
                }
            )
        )

    async def send_error(self, message):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat.error",
                    "message": message,
                }
            )
        )

    @database_sync_to_async
    def user_has_chat_access(self):
        return (
            get_chat_booking_for_user_id(
                user_id=getattr(self.user, "id", None),
                booking_id=self.booking_id,
            )
            is not None
        )
