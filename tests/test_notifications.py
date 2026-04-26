from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.schemas import NotificationResponse, NotificationType
from tests.factories import make_user, notification_response

SEND_URL = "/notifications/send"
DISPATCH_URL = "/notifications/dispatch"
LIST_URL = "/notifications/"


# ---------------------------------------------------------------------------
# POST /notifications/send
# ---------------------------------------------------------------------------


class TestSendEmail:
    @pytest.mark.asyncio
    async def test_send_email_success(self, admin_client):
        client = await admin_client()

        mock_resend_result = {"id": "msg_abc123"}
        mock_notification = NotificationResponse(**{
            **notification_response(resend_id="msg_abc123"),
            "id": uuid4(),
        })

        with (
            patch("app.routers.notifications.resend") as mock_resend,
            patch("app.routers.notifications.notification_crud") as mock_crud,
        ):
            mock_resend.Emails.send.return_value = mock_resend_result
            mock_crud.log_sent = AsyncMock(return_value=mock_notification)

            resp = await client.post(SEND_URL, json={
                "to": "user@example.com",
                "subject": "Booking Confirmed",
                "html": "<h1>Your booking is confirmed!</h1>",
                "template": "booking_confirmed",
                "triggered_by": "bookings-ms",
            })

        assert resp.status_code == 201
        data = resp.json()
        assert data["resend_id"] == "msg_abc123"
        assert data["status"] == "sent"

        mock_resend.Emails.send.assert_called_once()
        mock_crud.log_sent.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_email_resend_failure_logs_error(self, admin_client):
        client = await admin_client()

        mock_notification = NotificationResponse(**{
            **notification_response(status="failed", resend_id=None, error="API error"),
            "id": uuid4(),
        })

        with (
            patch("app.routers.notifications.resend") as mock_resend,
            patch("app.routers.notifications.notification_crud") as mock_crud,
        ):
            mock_resend.Emails.send.side_effect = Exception("API error")
            mock_crud.log_failed = AsyncMock(return_value=mock_notification)

            resp = await client.post(SEND_URL, json={
                "to": "user@example.com",
                "subject": "Test",
                "html": "<p>test</p>",
            })

        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "failed"
        assert data["error"] == "API error"
        mock_crud.log_failed.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_email_requires_admin_scope(self, client_factory):
        user = make_user(scopes="bookings:read")
        client = await client_factory(user)

        resp = await client.post(SEND_URL, json={
            "to": "user@example.com",
            "subject": "Test",
            "html": "<p>test</p>",
        })

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_send_email_no_auth_returns_422(self, anon_app):
        client = await anon_app()

        resp = await client.post(SEND_URL, json={
            "to": "user@example.com",
            "subject": "Test",
            "html": "<p>test</p>",
        })

        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /notifications/dispatch
# ---------------------------------------------------------------------------


class TestDispatchNotification:
    @pytest.mark.asyncio
    async def test_dispatch_booking_created_guest(self, admin_client):
        client = await admin_client()

        mock_resend_result = {"id": "msg_xyz789"}
        mock_notification = NotificationResponse(**{
            **notification_response(resend_id="msg_xyz789", template="booking_created_guest"),
            "id": uuid4(),
        })

        with (
            patch("app.routers.notifications.resend") as mock_resend,
            patch("app.routers.notifications.notification_crud") as mock_crud,
        ):
            mock_resend.Emails.send.return_value = mock_resend_result
            mock_crud.log_sent = AsyncMock(return_value=mock_notification)

            resp = await client.post(DISPATCH_URL, json={
                "notification_type": "booking_created_guest",
                "to": "guest@example.com",
                "data": {
                    "property_name": "Cozy Apartment",
                    "start_date": "2025-06-01",
                    "end_date": "2025-06-05",
                },
                "triggered_by": "bookings-ms",
            })

        assert resp.status_code == 201
        data = resp.json()
        assert data["resend_id"] == "msg_xyz789"
        assert data["template"] == "booking_created_guest"
        assert data["status"] == "sent"

        call_args = mock_resend.Emails.send.call_args
        sent_params = call_args[0][0]
        assert sent_params["subject"] == "Booking received — Cozy Apartment"
        assert "Cozy Apartment" in sent_params["html"]

    @pytest.mark.asyncio
    async def test_dispatch_payment_receipt(self, admin_client):
        client = await admin_client()

        mock_resend_result = {"id": "msg_abc456"}
        mock_notification = NotificationResponse(**{
            **notification_response(resend_id="msg_abc456", template="payment_receipt"),
            "id": uuid4(),
        })

        with (
            patch("app.routers.notifications.resend") as mock_resend,
            patch("app.routers.notifications.notification_crud") as mock_crud,
        ):
            mock_resend.Emails.send.return_value = mock_resend_result
            mock_crud.log_sent = AsyncMock(return_value=mock_notification)

            resp = await client.post(DISPATCH_URL, json={
                "notification_type": "payment_receipt",
                "to": "customer@example.com",
                "triggered_by": "payments-ms",
            })

        assert resp.status_code == 201
        data = resp.json()
        assert data["template"] == "payment_receipt"
        assert data["status"] == "sent"

        call_args = mock_resend.Emails.send.call_args
        sent_params = call_args[0][0]
        assert "payment" in sent_params["subject"].lower()

    @pytest.mark.asyncio
    async def test_dispatch_requires_admin_scope(self, client_factory):
        user = make_user(scopes="bookings:read")
        client = await client_factory(user)

        resp = await client.post(DISPATCH_URL, json={
            "notification_type": "payment_receipt",
            "to": "user@example.com",
        })

        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /notifications/
# ---------------------------------------------------------------------------


class TestListNotifications:
    @pytest.mark.asyncio
    async def test_list_notifications_admin(self, admin_client):
        client = await admin_client()

        mock_items = [
            NotificationResponse(**{
                **notification_response(),
                "id": uuid4(),
            })
            for _ in range(3)
        ]

        with patch("app.routers.notifications.notification_crud") as mock_crud:
            mock_crud.list_notifications = AsyncMock(return_value=mock_items)

            resp = await client.get(LIST_URL)

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_list_notifications_requires_admin(self, client_factory):
        user = make_user(scopes="bookings:read")
        client = await client_factory(user)

        resp = await client.get(LIST_URL)

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_notifications_no_auth_returns_422(self, anon_app):
        client = await anon_app()

        resp = await client.get(LIST_URL)

        assert resp.status_code == 422
