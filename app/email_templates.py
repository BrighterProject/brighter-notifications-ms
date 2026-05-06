from typing import Any

from loguru import logger

from app import settings
from app.mjml_renderer import render_mjml_template
from app.schemas import NotificationType

_TEMPLATE_MAP: dict[NotificationType, str] = {
    NotificationType.BOOKING_CREATED_GUEST: "booking_created_guest",
    NotificationType.BOOKING_CREATED_OWNER: "booking_created_owner",
    NotificationType.BOOKING_CONFIRMED: "booking_confirmed",
    NotificationType.BOOKING_CANCELLED: "booking_cancelled",
    NotificationType.PAYMENT_RECEIPT: "payment_receipt",
    NotificationType.PROPERTY_APPROVED: "property_approved",
}


def _build_url_vars(data: dict[str, Any]) -> dict[str, str]:
    """Build URL placeholder values derived from FRONTEND_BASE_URL and booking/property ids.

    Args:
        data: Caller-supplied data dict, used to extract booking_id and property_id.

    Returns:
        Dict of URL variable names to fully-qualified URL strings.
    """
    base = settings.frontend_base_url.rstrip("/")
    booking_id = data.get("booking_id", "")
    property_id = data.get("property_id", "")
    property_suffix = f"/{property_id}" if property_id else ""
    return {
        "help_url": f"{base}/help",
        "unsubscribe_url": f"{base}/unsubscribe",
        "privacy_url": f"{base}/privacy",
        "view_booking_url": f"{base}/bookings",
        "browse_properties_url": f"{base}/properties",
        "dashboard_url": f"{base}/admin/dashboard",
        "owner_dashboard_url": f"{base}/admin/dashboard",
        "view_listing_url": f"{base}/properties{property_suffix}",
        "host_guide_url": f"{base}/help/host-guide",
        "best_practices_url": f"{base}/help/best-practices",
        "approve_url": f"{base}/admin/dashboard",
        "decline_url": f"{base}/admin/dashboard",
        "contact_owner_url": f"{base}/bookings",
        "house_rules_url": f"{base}/properties{property_suffix}",
        "property_url": f"{base}/properties{property_suffix}",
        "download_receipt_url": f"{base}/bookings",
    }


_CHECKIN_FROM: dict[str, str] = {"bg": "от", "en": "from"}
_CHECKOUT_BY: dict[str, str] = {"bg": "до", "en": "by"}


def _build_computed_vars(
    notification_type: NotificationType, data: dict[str, Any], locale: str = "en"
) -> dict[str, str]:
    """Build computed placeholder values that replace former {{#if}} conditionals.

    These are derived from the caller data at render time; the MJML templates
    use plain {{key}} placeholders for them.

    Args:
        notification_type: Determines which computed vars are needed.
        data: Caller-supplied data dict.
        locale: Two-letter locale code used to localise inline strings.

    Returns:
        Dict of computed placeholder names to substitution strings.
    """
    computed: dict[str, str] = {}

    if notification_type is NotificationType.BOOKING_CONFIRMED:
        start_date = str(data.get("start_date", ""))
        end_date = str(data.get("end_date", ""))
        check_in_time = data.get("check_in_time") or ""
        check_out_time = data.get("check_out_time") or ""
        from_word = _CHECKIN_FROM.get(locale, _CHECKIN_FROM["en"])
        by_word = _CHECKOUT_BY.get(locale, _CHECKOUT_BY["en"])
        computed["checkin_display"] = (
            f"{start_date} {from_word} {check_in_time}" if check_in_time else start_date
        )
        computed["checkout_display"] = (
            f"{end_date} {by_word} {check_out_time}" if check_out_time else end_date
        )

    if notification_type is NotificationType.PAYMENT_RECEIPT:
        currency = str(data.get("currency", ""))
        cleaning_fee = data.get("cleaning_fee")
        service_fee = data.get("service_fee")
        computed["cleaning_fee_row"] = (
            f'<tr style="border-bottom: 1px solid #e2e8f0;">'
            f'<td style="padding: 12px 12px 12px 0; color: #475569;">Cleaning Fee</td>'
            f'<td style="padding: 12px 12px 12px; text-align: right; color: #475569;">'
            f"{currency} {cleaning_fee}</td></tr>"
        ) if cleaning_fee else ""
        computed["service_fee_row"] = (
            f'<tr style="border-bottom: 1px solid #e2e8f0;">'
            f'<td style="padding: 12px 12px 12px 0; color: #475569;">Service Fee</td>'
            f'<td style="padding: 12px 12px 12px; text-align: right; color: #475569;">'
            f"{currency} {service_fee}</td></tr>"
        ) if service_fee else ""

    return computed


def _resolve_template(base_name: str, locale: str) -> str:
    """Return the localised template name if it exists, else the base.

    Args:
        base_name: Template stem without locale suffix (e.g. "booking_confirmed").
        locale: Two-letter locale code (e.g. "bg", "en").

    Returns:
        Template stem to look up in the cache.
    """
    if locale == "bg":
        candidate = f"{base_name}_bg"
        from app.mjml_renderer import _TEMPLATE_CACHE  # noqa: PLC0415
        if candidate in _TEMPLATE_CACHE:
            return candidate
    return base_name


def render(
    notification_type: NotificationType,
    data: dict[str, Any],
    locale: str | None = None,
) -> tuple[str, str]:
    """Render email content for a given notification type.

    Args:
        notification_type: The type of notification to render.
        data: Template variable values supplied by the caller.
        locale: Two-letter locale code; "bg" uses Bulgarian templates,
            everything else falls back to English.

    Returns:
        (subject, html) tuple.

    Raises:
        ValueError: If notification_type is not recognised.
    """
    if notification_type not in _TEMPLATE_MAP:
        raise ValueError(f"Unknown notification type: {notification_type}")

    resolved_locale = locale if locale == "bg" else "en"
    base_name = _TEMPLATE_MAP[notification_type]
    template_name = _resolve_template(base_name, resolved_locale)

    # Merge order: url_vars < computed_vars < caller data (caller takes precedence)
    merged_data = {
        **_build_url_vars(data),
        **_build_computed_vars(notification_type, data, resolved_locale),
        **data,
    }

    try:
        subject, html = render_mjml_template(template_name, merged_data)
        logger.debug(
            "Rendered email template: type={} template={} subject={!r}",
            notification_type,
            template_name,
            subject,
        )
        return subject, html
    except Exception as e:
        logger.error(
            "Failed to render email template: type={} template={} error={}",
            notification_type,
            template_name,
            e,
        )
        raise
