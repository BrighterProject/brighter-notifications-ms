from typing import Any

from loguru import logger

from app import settings
from app.mjml_renderer import render_mjml_template
from app.schemas import NotificationType


def _build_url_vars(data: dict[str, Any]) -> dict[str, str]:
    base = settings.frontend_base_url.rstrip("/")
    booking_id = data.get("booking_id", "")
    property_id = data.get("property_id", "")
    return {
        "help_url": f"{base}/help",
        "unsubscribe_url": f"{base}/unsubscribe",
        "privacy_url": f"{base}/privacy",
        "view_booking_url": f"{base}/bookings/{booking_id}" if booking_id else f"{base}/bookings",
        "browse_properties_url": f"{base}/properties",
        "dashboard_url": f"{base}/dashboard",
        "owner_dashboard_url": f"{base}/dashboard",
        "view_listing_url": f"{base}/properties/{property_id}" if property_id else f"{base}/properties",
        "host_guide_url": f"{base}/help/host-guide",
        "best_practices_url": f"{base}/help/best-practices",
        "approve_url": f"{base}/bookings/{booking_id}/confirm" if booking_id else f"{base}/dashboard",
        "decline_url": f"{base}/bookings/{booking_id}/cancel" if booking_id else f"{base}/dashboard",
        "contact_owner_url": f"{base}/bookings/{booking_id}/contact" if booking_id else f"{base}/bookings",
        "house_rules_url": f"{base}/properties/{property_id}/rules" if property_id else f"{base}/properties",
        "property_url": f"{base}/properties/{property_id}" if property_id else f"{base}/properties",
        "download_receipt_url": f"{base}/bookings/{booking_id}/receipt" if booking_id else f"{base}/bookings",
    }


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

    # URL vars are injected automatically; caller data takes precedence to allow override
    merged_data = {**_build_url_vars(data), **data}

    try:
        subject, html = render_mjml_template(template_name, merged_data)
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
