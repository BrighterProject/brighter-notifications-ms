from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationChannel(StrEnum):
    EMAIL = "email"


class NotificationStatus(StrEnum):
    SENT = "sent"
    FAILED = "failed"


class NotificationType(StrEnum):
    BOOKING_CREATED_GUEST = "booking_created_guest"
    BOOKING_CREATED_OWNER = "booking_created_owner"
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    PAYMENT_RECEIPT = "payment_receipt"
    PROPERTY_APPROVED = "property_approved"


class NotificationResponse(BaseModel):
    id: UUID
    channel: NotificationChannel
    recipient: str
    subject: str
    template: str
    status: NotificationStatus
    resend_id: str | None
    error: str | None
    triggered_by: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    html: str
    template: str = "generic"
    triggered_by: str | None = None


class DispatchRequest(BaseModel):
    notification_type: NotificationType
    to: str
    data: dict[str, Any] = {}
    triggered_by: str | None = None
