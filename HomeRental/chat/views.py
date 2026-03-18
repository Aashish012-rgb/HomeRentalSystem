from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_chat_booking_for_user


@login_required
def chat_room(request, booking_id):
    """Render the booking chat page for accepted-booking participants only."""
    booking = get_chat_booking_for_user(request.user, booking_id)
    chat_messages = booking.chat_messages.select_related("sender")

    return render(
        request,
        "chat/chat_room.html",
        {
            "booking": booking,
            "chat_messages": chat_messages,
            "chat_bootstrap": {
                "bookingId": booking.id,
                "currentUserId": request.user.id,
            },
        },
    )
