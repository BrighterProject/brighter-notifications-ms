from enum import StrEnum

from ms_core import AbstractModel as Model
from tortoise import fields


class NotificationChannel(StrEnum):
    EMAIL = "email"


class NotificationStatus(StrEnum):
    SENT = "sent"
    FAILED = "failed"


class Notification(Model):
    id = fields.UUIDField(primary_key=True)

    channel = fields.CharEnumField(NotificationChannel, default=NotificationChannel.EMAIL)
    recipient = fields.CharField(max_length=255)  # email address
    subject = fields.CharField(max_length=500)
    template = fields.CharField(max_length=100)  # e.g. "booking_confirmed"

    status = fields.CharEnumField(NotificationStatus, default=NotificationStatus.SENT)
    resend_id = fields.CharField(max_length=255, null=True)  # Resend message ID
    error = fields.TextField(null=True)

    # Who/what triggered this notification
    triggered_by = fields.CharField(max_length=100, null=True)  # e.g. "bookings-ms"

    class Meta:  # type: ignore
        table = "notifications"
        ordering = ["-created_at"]
