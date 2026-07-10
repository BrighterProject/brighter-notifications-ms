import pytest

from app.email_templates import render
from app.schemas import NotificationType


class TestMJMLTemplates:
    """Test MJML email template rendering."""

    def test_booking_created_guest(self):
        """Test guest booking notification template."""
        data = {
            "property_name": "Sunny Beach Villa",
            "start_date": "2026-05-15",
            "end_date": "2026-05-22",
            "view_booking_url": "https://brighter.bg/bookings/123",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.BOOKING_CREATED_GUEST, data)

        assert "Booking Received" in subject
        assert "Sunny Beach Villa" in html
        assert "2026-05-15" in html
        assert "2026-05-22" in html
        assert "view-booking-url" not in html  # variables should be replaced
        assert len(html) > 1000  # should be substantial HTML

    def test_booking_created_owner(self):
        """Test owner booking notification template."""
        data = {
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

        subject, html = render(NotificationType.BOOKING_CREATED_OWNER, data)

        assert "New Booking Request" in subject
        assert "Mountain Retreat" in html
        assert "Confirm Booking" in html or "confirm" in html.lower()
        assert len(html) > 1000

    def test_booking_confirmed(self):
        """Test booking confirmation template."""
        data = {
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
            "view_booking_url": "https://brighter.bg/bookings/123",
            "property_url": "https://brighter.bg/properties/456",
            "contact_owner_url": "https://brighter.bg/contact/owner",
            "house_rules_url": "https://brighter.bg/rules",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.BOOKING_CONFIRMED, data)

        assert "Confirmed" in subject
        assert "BK-2026-123456" in html
        assert "City Center Apartment" in html
        assert "1400" in html
        assert len(html) > 1000

    def test_booking_cancelled(self):
        """Test booking cancellation template."""
        data = {
            "booking_id": "BK-2026-789012",
            "property_name": "Coastal House",
            "start_date": "2026-08-01",
            "end_date": "2026-08-08",
            "cancelled_date": "2026-07-20",
            "currency": "EUR",
            "refund_amount": "1200",
            "browse_properties_url": "https://brighter.bg/search",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.BOOKING_CANCELLED, data)

        assert "Cancelled" in subject
        assert "Coastal House" in html
        assert "1200" in html
        assert len(html) > 1000

    def test_payment_receipt(self):
        """Test payment receipt template."""
        data = {
            "receipt_id": "RC-2026-555",
            "payment_date": "2026-07-15",
            "property_name": "Lakeside Cabin",
            "start_date": "2026-08-15",
            "end_date": "2026-08-22",
            "num_nights": 7,
            "num_guests": 2,
            "currency": "EUR",
            "room_rate": "800",
            "cleaning_fee": "100",
            "service_fee": "120",
            "total_amount": "1020",
            "payment_method": "Visa ending in 4242",
            "view_booking_url": "https://brighter.bg/bookings/123",
            "download_receipt_url": "https://brighter.bg/receipts/555",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.PAYMENT_RECEIPT, data)

        assert "Payment" in subject
        assert "RC-2026-555" in html
        assert "Lakeside Cabin" in html
        assert "1020" in html
        assert len(html) > 1000

    def test_property_approved(self):
        """Test property approval template."""
        data = {
            "property_name": "Luxury Penthouse",
            "property_city": "Sofia",
            "property_type": "Apartment",
            "max_guests": 6,
            "view_listing_url": "https://brighter.bg/listings/789",
            "owner_dashboard_url": "https://brighter.bg/dashboard",
            "host_guide_url": "https://brighter.bg/guides/host",
            "best_practices_url": "https://brighter.bg/guides/practices",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.PROPERTY_APPROVED, data)

        assert "Approved" in subject
        assert "Luxury Penthouse" in html
        assert "Sofia" in html
        assert len(html) > 1000

    def test_checkin_link(self):
        """Check-in link template renders the encrypted-messaging lobby email."""
        data = {
            "token": "eyJhbGciOiJIUzI1NiJ9.abc.def",
            "num_guests": 4,
            "checkin_url": "https://brighter.bg/checkin/eyJhbGciOiJIUzI1NiJ9.abc.def",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.CHECKIN_LINK, data)

        assert "Check-in" in subject or "check-in" in subject.lower()
        assert "https://brighter.bg/checkin/eyJhbGciOiJIUzI1NiJ9.abc.def" in html
        assert "encrypted" in html.lower()
        assert "{{" not in html  # no leftover placeholders
        assert len(html) > 1000

    def test_checkin_link_bg_locale(self):
        """Bulgarian check-in link template is selected for the bg locale."""
        data = {
            "token": "tok123",
            "num_guests": 2,
            "checkin_url": "https://brighter.bg/checkin/tok123",
        }
        subject, html = render(NotificationType.CHECKIN_LINK, data, locale="bg")
        assert "https://brighter.bg/checkin/tok123" in html
        assert len(html) > 1000

    def test_checkin_link_url_computed_from_token(self):
        """checkin_url is derived from token + FRONTEND_BASE_URL when not passed."""
        data = {"token": "rawtoken", "num_guests": 1}
        _, html = render(NotificationType.CHECKIN_LINK, data)
        assert "/checkin/rawtoken" in html

    def test_booking_confirmed_checkin_with_time(self):
        """Check-in display includes time when check_in_time is provided."""
        data = {
            "booking_id": "BK-001",
            "property_name": "Villa",
            "start_date": "2026-07-10",
            "end_date": "2026-07-17",
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "num_guests": 2,
            "num_nights": 7,
            "total_price": "700",
            "currency": "EUR",
        }
        _, html = render(NotificationType.BOOKING_CONFIRMED, data)
        assert "2026-07-10 from 15:00" in html
        assert "2026-07-17 by 11:00" in html

    def test_booking_confirmed_checkin_without_time(self):
        """Check-in display shows only date when check_in_time is absent."""
        data = {
            "booking_id": "BK-002",
            "property_name": "Villa",
            "start_date": "2026-07-10",
            "end_date": "2026-07-17",
            "num_guests": 2,
            "num_nights": 7,
            "total_price": "700",
            "currency": "EUR",
        }
        _, html = render(NotificationType.BOOKING_CONFIRMED, data)
        assert "2026-07-10" in html
        assert "from" not in html or "2026-07-10 from" not in html
        assert "2026-07-17" in html
        assert "by" not in html or "2026-07-17 by" not in html

    def test_payment_receipt_with_optional_fees(self):
        """Both fee rows render when cleaning_fee and service_fee are provided."""
        data = {
            "receipt_id": "RC-001",
            "payment_date": "2026-07-15",
            "property_name": "Cabin",
            "start_date": "2026-08-01",
            "end_date": "2026-08-08",
            "num_nights": 7,
            "num_guests": 2,
            "currency": "EUR",
            "room_rate": "700",
            "cleaning_fee": "50",
            "service_fee": "30",
            "total_amount": "780",
            "payment_method": "Visa",
        }
        _, html = render(NotificationType.PAYMENT_RECEIPT, data)
        assert "Cleaning Fee" in html
        assert "EUR 50" in html
        assert "Service Fee" in html
        assert "EUR 30" in html

    def test_payment_receipt_without_optional_fees(self):
        """Fee rows are absent when cleaning_fee and service_fee are not provided."""
        data = {
            "receipt_id": "RC-002",
            "payment_date": "2026-07-15",
            "property_name": "Cabin",
            "start_date": "2026-08-01",
            "end_date": "2026-08-08",
            "num_nights": 7,
            "num_guests": 2,
            "currency": "EUR",
            "room_rate": "700",
            "total_amount": "700",
            "payment_method": "Visa",
        }
        _, html = render(NotificationType.PAYMENT_RECEIPT, data)
        assert "Cleaning Fee" not in html
        assert "Service Fee" not in html

    def test_payment_receipt_with_only_cleaning_fee(self):
        """Only cleaning fee row renders when service_fee is absent."""
        data = {
            "receipt_id": "RC-003",
            "payment_date": "2026-07-15",
            "property_name": "Cabin",
            "start_date": "2026-08-01",
            "end_date": "2026-08-08",
            "num_nights": 7,
            "num_guests": 2,
            "currency": "EUR",
            "room_rate": "700",
            "cleaning_fee": "60",
            "total_amount": "760",
            "payment_method": "Visa",
        }
        _, html = render(NotificationType.PAYMENT_RECEIPT, data)
        assert "Cleaning Fee" in html
        assert "EUR 60" in html
        assert "Service Fee" not in html

    def test_booking_cancelled_substitutes_refund_amount(self):
        """A supplied refund_amount replaces its placeholder."""
        data = {
            "booking_id": "BK-001",
            "property_name": "Test Apartment Sofia",
            "start_date": "17 June 2026",
            "end_date": "21 June 2026",
            "cancelled_date": "16 June 2026",
            "currency": "EUR",
            "refund_amount": "150.00",
        }
        _, html = render(NotificationType.BOOKING_CANCELLED, data)
        assert "EUR 150.00" in html
        assert "{{refund_amount}}" not in html

    def test_unsupplied_placeholder_is_stripped(self):
        """Missing fields must not leak raw {{key}} tokens into the email."""
        data = {
            "booking_id": "BK-002",
            "property_name": "Test Apartment Sofia",
            "start_date": "17 June 2026",
            "end_date": "21 June 2026",
            "cancelled_date": "16 June 2026",
            "currency": "EUR",
            # refund_amount intentionally omitted
        }
        _, html = render(NotificationType.BOOKING_CANCELLED, data)
        assert "{{" not in html
        assert "refund_amount" not in html

    def test_invalid_notification_type(self):
        """Test that invalid notification types raise an error."""
        with pytest.raises(ValueError, match="Unknown notification type"):
            render("invalid_type", {})  # type: ignore

    def test_html_structure(self):
        """Test that rendered HTML is well-formed."""
        data = {
            "property_name": "Test Property",
            "start_date": "2026-05-01",
            "end_date": "2026-05-07",
            "view_booking_url": "https://brighter.bg/bookings/123",
            "help_url": "https://brighter.bg/help",
            "unsubscribe_url": "https://brighter.bg/unsubscribe",
            "privacy_url": "https://brighter.bg/privacy",
        }

        subject, html = render(NotificationType.BOOKING_CREATED_GUEST, data)

        # Basic HTML structure checks
        assert html.lower().startswith("<!doctype html")
        assert "<html" in html
        assert "</html>" in html
        assert "<body" in html
        assert "</body>" in html
        assert len(html) < 150000  # should be under Gmail's 102KB limit (after minification)
