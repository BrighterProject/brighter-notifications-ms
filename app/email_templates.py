from typing import Any

from loguru import logger

from app.mjml_renderer import render_mjml_template
from app.schemas import NotificationType


def render(notification_type: NotificationType, data: dict[str, Any]) -> tuple[str, str]:
    """
    Render email content (subject, html) for a given notification type and data.
    Uses MJML templates with Handlebars variable substitution.
    Returns (subject, html) tuple.
    """
    template_map = {
        NotificationType.BOOKING_CREATED_GUEST: "booking_created_guest",
        NotificationType.BOOKING_CREATED_OWNER: "booking_created_owner",
        NotificationType.BOOKING_CONFIRMED: "booking_confirmed",
        NotificationType.BOOKING_CANCELLED: "booking_cancelled",
        NotificationType.PAYMENT_RECEIPT: "payment_receipt",
        NotificationType.PROPERTY_APPROVED: "property_approved",
    }

    if notification_type not in template_map:
        raise ValueError(f"Unknown notification type: {notification_type}")

    template_name = template_map[notification_type]

    try:
        subject, html = render_mjml_template(template_name, data)
        logger.debug(
            "Rendered MJML template: type={} template={} subject={!r}",
            notification_type,
            template_name,
            subject,
        )
        return subject, html
    except Exception as e:
        logger.error(
            "Failed to render MJML template: type={} template={} error={}",
            notification_type,
            template_name,
            e,
        )
        raise
