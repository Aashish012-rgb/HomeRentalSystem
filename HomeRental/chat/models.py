from django.conf import settings
from django.db import models

from home.models import Booking


class ChatMessage(models.Model):
    """Single chat message stored against an accepted booking."""

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_chat_messages",
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")
        indexes = [
            models.Index(fields=["booking", "created_at"]),
        ]

    def __str__(self):
        return f"Message #{self.pk} for booking #{self.booking_id}"
