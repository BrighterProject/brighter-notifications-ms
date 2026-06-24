from email.message import EmailMessage
from unittest.mock import AsyncMock, patch

import pytest

from app import email_transport
from app.email_transport import ResendTransport, SmtpTransport, get_transport


class TestGetTransport:
    def test_selects_smtp_when_configured(self):
        with patch.object(email_transport.settings, "email_transport", "smtp"):
            assert isinstance(get_transport(), SmtpTransport)

    def test_selects_resend_by_default(self):
        with patch.object(email_transport.settings, "email_transport", "resend"):
            assert isinstance(get_transport(), ResendTransport)


class TestResendTransport:
    @pytest.mark.asyncio
    async def test_send_returns_resend_id(self):
        with patch.object(email_transport, "resend") as mock_resend:
            mock_resend.Emails.send.return_value = {"id": "re_123"}

            message_id = await ResendTransport().send(
                to="user@example.com", subject="Hi", html="<p>hi</p>"
            )

        assert message_id == "re_123"
        params = mock_resend.Emails.send.call_args[0][0]
        assert params["to"] == ["user@example.com"]
        assert params["subject"] == "Hi"
        assert params["html"] == "<p>hi</p>"


class TestSmtpTransport:
    @pytest.mark.asyncio
    async def test_send_builds_html_message_to_mailpit(self):
        with (
            patch.object(email_transport, "aiosmtplib") as mock_smtp,
            patch.object(email_transport.settings, "smtp_host", "mailpit"),
            patch.object(email_transport.settings, "smtp_port", 1025),
            patch.object(email_transport.settings, "smtp_starttls", False),
        ):
            mock_smtp.send = AsyncMock()

            message_id = await SmtpTransport().send(
                to="user@example.com", subject="Verify", html="<a>link</a>"
            )

        assert message_id  # synthetic Message-ID returned for logging
        mock_smtp.send.assert_awaited_once()
        sent_message, kwargs = mock_smtp.send.call_args
        message: EmailMessage = sent_message[0]
        assert isinstance(message, EmailMessage)
        assert message["To"] == "user@example.com"
        assert message["Subject"] == "Verify"
        assert kwargs == {"hostname": "mailpit", "port": 1025, "start_tls": False}
        # HTML body is delivered as an alternative part
        html_part = message.get_body(preferencelist=("html",))
        assert html_part is not None
        assert "<a>link</a>" in html_part.get_content()
