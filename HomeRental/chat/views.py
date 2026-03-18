from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_chat_booking_for_user


@login_required
def chat_room(request, booking_id):
    # Reuse the shared service so page access follows the same rules as websocket chat.
    booking = get_chat_booking_for_user(request.user, booking_id)
    # Opening the room marks incoming messages as read for the current participant.
    booking.chat_messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
    # Match the current model field name when loading message history.
    chat_messages = booking.chat_messages.select_related("sender")

    return render(
        request,
        "chat/chat_room.html",
        {
            "booking": booking,
            "chat_messages": chat_messages,
            "user_id": request.user.id,
        },
    )
