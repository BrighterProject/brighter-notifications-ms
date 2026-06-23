"""Pluggable email transports.

Production delivers through Resend's HTTPS API; dev/e2e delivers through SMTP to
a local mailpit sink. The active transport is chosen from ``settings.email_transport``.
"""

from __future__ import annotations

from email.message import EmailMessage
from email.utils import make_msgid
from typing import Protocol

import aiosmtplib
import resend

from app import settings


class EmailTransport(Protocol):
    """Delivers a single HTML email and returns a provider message id."""

    async def send(self, *, to: str, subject: str, html: str) -> str: ...


class ResendTransport:
    """Delivers via Resend's HTTPS API (production default)."""

    async def send(self, *, to: str, subject: str, html: str) -> str:
        params: resend.Emails.SendParams = {
            "from": settings.default_from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        result = resend.Emails.send(params)
        return result["id"] if isinstance(result, dict) else result.id  # type: ignore


class SmtpTransport:
    """Delivers via SMTP — used in dev/e2e to reach the mailpit sink."""

    async def send(self, *, to: str, subject: str, html: str) -> str:
        message = EmailMessage()
        message["From"] = settings.default_from_email
        message["To"] = to
        message["Subject"] = subject
        message_id = make_msgid()
        message["Message-ID"] = message_id
        message.set_content("This email requires an HTML-capable client.")
        message.add_alternative(html, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=settings.smtp_starttls,
        )
        return message_id


def get_transport() -> EmailTransport:
    """Return the transport selected by ``settings.email_transport``."""
    if settings.email_transport == "smtp":
        return SmtpTransport()
    return ResendTransport()
