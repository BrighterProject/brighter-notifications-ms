from typing import Any

from app.schemas import NotificationType


def render(notification_type: NotificationType, data: dict[str, Any]) -> tuple[str, str]:
    """
    Render email content (subject, html) for a given notification type and data.
    Returns (subject, html) tuple.
    """
    if notification_type == NotificationType.BOOKING_CREATED_GUEST:
        property_name = data.get("property_name", "property")
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        date_range = f"{start_date} – {end_date}"
        return (
            f"Booking received — {property_name}",
            f"<p>Your booking for <strong>{property_name}</strong> "
            f"({date_range}) has been received and is awaiting confirmation.</p>",
        )

    elif notification_type == NotificationType.BOOKING_CREATED_OWNER:
        property_name = data.get("property_name", "property")
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        date_range = f"{start_date} – {end_date}"
        return (
            f"New booking request — {property_name}",
            f"<p>A new booking has been placed for <strong>{property_name}</strong> "
            f"({date_range}). Please review and confirm or cancel it.</p>",
        )

    elif notification_type == NotificationType.BOOKING_CONFIRMED:
        return (
            "Your booking has been confirmed",
            "<p>Great news! Your booking has been <strong>confirmed</strong>. "
            "We look forward to welcoming you.</p>",
        )

    elif notification_type == NotificationType.BOOKING_CANCELLED:
        return (
            "Your booking has been cancelled",
            "<p>Your booking has been <strong>cancelled</strong>. "
            "If you have any questions, please contact us.</p>",
        )

    elif notification_type == NotificationType.PAYMENT_RECEIPT:
        return (
            "Payment received — Thank you!",
            "<p>We have received your payment. "
            "Your booking is now pending owner confirmation.</p>",
        )

    elif notification_type == NotificationType.PROPERTY_APPROVED:
        return (
            "Your property has been approved",
            "<p>Great news! Your property listing has been reviewed and "
            "<strong>approved</strong> by our team. It is now live and visible to guests.</p>",
        )

    else:
        raise ValueError(f"Unknown notification type: {notification_type}")
