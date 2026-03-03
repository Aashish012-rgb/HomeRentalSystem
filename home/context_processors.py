from .models import (
    Booking,
    BookingCancellationNotification,
    BookingAcceptanceNotification,
)


def unread_notifications_count(request):
    if not request.user.is_authenticated:
        return {
            "unread_notifications_count": 0,
            "recent_notifications": [],
        }

    owner_notifications = Booking.objects.filter(owner=request.user).select_related(
        "booked_by", "property"
    )
    tenant_notifications = BookingCancellationNotification.objects.filter(
        tenant=request.user
    ).select_related("owner", "property")
    tenant_acceptance = BookingAcceptanceNotification.objects.filter(
        tenant=request.user
    ).select_related("owner", "property")

    owner_recent = [
        {
            "message": f"{item.booked_by.username} booked {item.property.title}",
            "url": f"/properties/{item.property.id}/?view=compact",
            "created_at": item.booked_at,
            "is_read": item.is_read,
        }
        for item in owner_notifications
    ]
    tenant_recent = [
        {
            "message": f"{item.owner.username} canceled your booking for {item.property.title}",
            "url": f"/properties/{item.property.id}/",
            "created_at": item.canceled_at,
            "is_read": item.is_read,
        }
        for item in tenant_notifications
    ]
    tenant_accepted_recent = [
        {
            "message": f"{item.owner.username} accepted your booking for {item.property.title}",
            "url": f"/properties/{item.property.id}/",
            "created_at": item.accepted_at,
            "is_read": item.is_read,
        }
        for item in tenant_acceptance
    ]

    recent = sorted(
        owner_recent + tenant_recent + tenant_accepted_recent,
        key=lambda n: n["created_at"],
        reverse=True,
    )[:5]
    count = (
        owner_notifications.filter(is_read=False).count()
        + tenant_notifications.filter(is_read=False).count()
        + tenant_acceptance.filter(is_read=False).count()
    )

    return {
        "unread_notifications_count": count,
        "recent_notifications": recent,
    }

