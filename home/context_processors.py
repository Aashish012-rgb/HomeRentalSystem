from .models import Booking


def unread_notifications_count(request):
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "recent_notifications": [],
        }

    owner_notifications = Booking.objects.filter(owner=request.user).select_related(
        "booked_by", "property"
    )
    count = owner_notifications.filter(is_read=False).count()
    recent = owner_notifications.order_by("-booked_at")[:5]

    return {
        "unread_notifications_count": count,
        "recent_notifications": recent,
    }



