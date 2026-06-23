"""
All test-data builders in one place.
Import from here in every test file — never define dummy data inline.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def make_user(scopes: str = "") -> dict:
    return {
        "id": str(uuid4()),
        "username": "testuser",
        "scopes": scopes,
    }


def make_admin() -> dict:
    return {
        "id": str(uuid4()),
        "username": "admin",
        "scopes": (
            "admin:scopes admin:notifications admin:notifications:read admin:notifications:write"
        ),
    }


def notification_response(
    *,
    recipient: str = "user@example.com",
    subject: str = "Test Subject",
    template: str = "generic",
    status: str = "sent",
    resend_id: str | None = "msg_123",
    error: str | None = None,
    triggered_by: str | None = "test",
) -> dict:
    return {
        "id": str(uuid4()),
        "channel": "email",
        "recipient": recipient,
        "subject": subject,
        "template": template,
        "status": status,
        "resend_id": resend_id,
        "error": error,
        "triggered_by": triggered_by,
        "created_at": datetime.now(UTC).isoformat(),
    }
