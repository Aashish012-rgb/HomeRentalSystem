import logging

logger = logging.getLogger(__name__)


def _email_notifications_disabled(*, subject: str, to_email: str = "") -> bool:
    logger.info(
        "Email notifications are disabled (subject=%s, to=%s).",
        subject,
        to_email,
    )
    return False


def send_booking_confirmation_email(request, booking) -> bool:
    return _email_notifications_disabled(
        subject="Booking Confirmation",
        to_email=getattr(getattr(booking, "booked_by", None), "email", ""),
    )


def send_booking_accepted_email(request, booking) -> bool:
    return _email_notifications_disabled(
        subject="Your Booking Has Been Accepted",
        to_email=getattr(getattr(booking, "booked_by", None), "email", ""),
    )


def send_booking_canceled_email(
    request,
    booking,
    *,
    cancellation_reason: str,
    refund_details: str,
) -> bool:
    return _email_notifications_disabled(
        subject="Booking Cancellation",
        to_email=getattr(getattr(booking, "booked_by", None), "email", ""),
    )
