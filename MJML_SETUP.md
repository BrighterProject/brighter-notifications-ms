# MJML Email Templates Setup

This document describes the MJML email template implementation for the Brighter notifications microservice.

## Overview

The notifications-ms now uses professional, responsive MJML email templates instead of plain HTML. All 6 notification types have been converted to beautiful, mobile-friendly templates with:

- Professional design with Brighter branding
- Responsive layout (mobile-optimized)
- Dark mode support
- Handlebars variable substitution
- Cross-client compatibility (Outlook, Gmail, Apple Mail, etc.)
- Minified output to stay under Gmail's 102KB clip limit

## Notification Types & Templates

| Notification Type | Template File | Description |
|---|---|---|
| `booking_created_guest` | `booking_created_guest.mjml` | Sent to guest when booking is received |
| `booking_created_owner` | `booking_created_owner.mjml` | Sent to owner when new booking request arrives |
| `booking_confirmed` | `booking_confirmed.mjml` | Sent to guest when booking is confirmed |
| `booking_cancelled` | `booking_cancelled.mjml` | Sent to guest when booking is cancelled |
| `payment_receipt` | `payment_receipt.mjml` | Sent to guest after payment is processed |
| `property_approved` | `property_approved.mjml` | Sent to owner when property is approved |

## Architecture

### File Structure

```
app/
  templates/
    emails/
      booking_created_guest.mjml
      booking_created_owner.mjml
      booking_confirmed.mjml
      booking_cancelled.mjml
      payment_receipt.mjml
      property_approved.mjml
  mjml_renderer.py        # MJML compilation module
  email_templates.py      # Updated to use MJML rendering
```

### How It Works

1. **Template Storage**: MJML templates are stored in `app/templates/emails/`
2. **Variable Substitution**: Templates use Handlebars syntax `{{variable_name}}` for dynamic content
3. **MJML Compilation**: Templates are compiled to HTML using the `mjml` CLI tool (Node.js)
4. **Email Sending**: Compiled HTML is sent via Resend API (existing flow unchanged)

## Usage

### Calling From Other Services

The `/notifications/dispatch` endpoint remains unchanged:

```python
# From bookings-ms, payments-ms, properties-ms
import httpx

async def send_booking_confirmation(to_email: str, booking_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notifications-ms:8004/notifications/dispatch",
            json={
                "notification_type": "booking_confirmed",
                "to": to_email,
                "data": booking_data,
                "triggered_by": "bookings-ms",
            },
            headers={"X-User-Id": "system", "X-User-Scopes": "admin:notifications:write"},
        )
```

### Template Variables

Each template requires specific variables in the `data` dict:

#### booking_created_guest
```python
{
    "property_name": "Sunny Beach Villa",
    "start_date": "2026-05-15",
    "end_date": "2026-05-22",
    "view_booking_url": "https://brighter.bg/bookings/123",
    "help_url": "https://brighter.bg/help",
    "unsubscribe_url": "https://brighter.bg/unsubscribe",
    "privacy_url": "https://brighter.bg/privacy",
}
```

#### booking_created_owner
```python
{
    "property_name": "Mountain Retreat",
    "start_date": "2026-06-01",
    "end_date": "2026-06-07",
    "approve_url": "https://brighter.bg/approve/123",
    "decline_url": "https://brighter.bg/decline/123",
    "dashboard_url": "https://brighter.bg/dashboard",
    "help_url": "https://brighter.bg/help",
    "unsubscribe_url": "https://brighter.bg/unsubscribe",
    "privacy_url": "https://brighter.bg/privacy",
}
```

#### booking_confirmed
```python
{
    "booking_id": "BK-2026-123456",
    "property_name": "City Center Apartment",
    "start_date": "2026-07-10",
    "end_date": "2026-07-17",
    "check_in_time": "15:00",
    "check_out_time": "11:00",
    "num_guests": 4,
    "num_nights": 7,
    "total_price": "1400",
    "currency": "EUR",
    "view_booking_url": "...",
    "property_url": "...",
    "contact_owner_url": "...",
    "house_rules_url": "...",
    "help_url": "...",
    "unsubscribe_url": "...",
    "privacy_url": "...",
}
```

#### booking_cancelled
```python
{
    "booking_id": "BK-2026-789012",
    "property_name": "Coastal House",
    "start_date": "2026-08-01",
    "end_date": "2026-08-08",
    "cancelled_date": "2026-07-20",
    "currency": "EUR",
    "refund_amount": "1200",
    "browse_properties_url": "...",
    "help_url": "...",
    "unsubscribe_url": "...",
    "privacy_url": "...",
}
```

#### payment_receipt
```python
{
    "receipt_id": "RC-2026-555",
    "payment_date": "2026-07-15",
    "property_name": "Lakeside Cabin",
    "start_date": "2026-08-15",
    "end_date": "2026-08-22",
    "num_nights": 7,
    "num_guests": 2,
    "currency": "EUR",
    "room_rate": "800",
    "cleaning_fee": "100",     # optional
    "service_fee": "120",      # optional
    "total_amount": "1020",
    "payment_method": "Visa ending in 4242",
    "view_booking_url": "...",
    "download_receipt_url": "...",
    "help_url": "...",
    "unsubscribe_url": "...",
    "privacy_url": "...",
}
```

#### property_approved
```python
{
    "property_name": "Luxury Penthouse",
    "property_city": "Sofia",
    "property_type": "Apartment",
    "max_guests": 6,
    "view_listing_url": "...",
    "owner_dashboard_url": "...",
    "host_guide_url": "...",
    "best_practices_url": "...",
    "help_url": "...",
    "unsubscribe_url": "...",
    "privacy_url": "...",
}
```

## Setup & Dependencies

### Node.js Dependencies

MJML is installed via `package.json`:

```bash
npm install
```

The `mjml` CLI tool is used to compile templates at runtime via `subprocess.run()`.

### Python Module

`app/mjml_renderer.py` provides:

- `compile_mjml(mjml_path: str) -> str` — Compiles MJML file to HTML
- `render_mjml_template(template_name: str, data: dict) -> tuple[str, str]` — Renders template with variables, returns (subject, html)

### Error Handling

If MJML compilation fails:
- `RuntimeError` is raised with the MJML validation error
- The error is logged via loguru at ERROR level
- The service returns HTTP 500 if rendering fails during email dispatch

## Testing

All templates are tested in `tests/test_mjml_templates.py`:

```bash
uv run pytest tests/test_mjml_templates.py -v
```

Tests verify:
- Templates compile without validation errors
- Dynamic variables are properly substituted
- HTML output is well-formed
- Output is under Gmail's 102KB limit (after minification)

## Design Details

### Brand Colors

- Primary: `#2563eb` (Blue) — CTAs, headers
- Success: `#16a34a` (Green) — Confirmations, approvals
- Warning: `#f59e0b` (Amber) — Pending actions
- Error: `#dc2626` (Red) — Cancellations
- Neutral: `#64748b` (Slate) — Body text
- Background: `#f8fafc` (Light Slate) — Page background

### Responsive Design

- Desktop: 600px width (standard email width)
- Mobile: Full viewport width with adjusted spacing
- Compiled with `--config.minify=true` for proper iOS stacking

### Dark Mode

All templates include dark mode support via CSS media queries:
- Light mode: Default light background, dark text
- Dark mode: Dark background, light text (when OS prefers dark)

## Performance

- Minified HTML size: ~40-60KB per email
- Compilation time: ~200-300ms per template (cached at module level)
- Gmail clip limit: ~102KB (we stay well under this)

## Backward Compatibility

The `/notifications/send` endpoint still works for custom subject+html (legacy support), but new code should use `/notifications/dispatch` with the template name and data dict.

## Future Enhancements

Potential improvements:

1. **Template Caching**: Cache compiled HTML for each template + data hash
2. **Handlebars Extensions**: Support conditional blocks `{{#if}}...{{/if}}`
3. **i18n**: Multi-language templates with locale-specific rendering
4. **A/B Testing**: Multiple variants of each template
5. **Preview URLs**: Generate preview URLs for testing before sending

## Debugging

### View Rendered MJML

To debug template rendering:

```python
from app.mjml_renderer import render_mjml_template

data = {"property_name": "Test", ...}
subject, html = render_mjml_template("booking_created_guest", data)
print(subject)
print(html[:500])  # First 500 chars
```

### Check MJML CLI

```bash
npx mjml --version
npx mjml app/templates/emails/booking_created_guest.mjml -o /tmp/test.html
```

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## References

- [MJML Documentation](https://mjml.io/documentation)
- [MJML Component Reference](https://mjml.io/try-it-live)
- [Email Client Support Matrix](https://www.campaignmonitor.com/css)
