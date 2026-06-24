from fastapi import APIRouter, Depends, status
from loguru import logger

from app import email_templates
from app.crud import notification_crud
from app.deps import can_read_notifications, can_send_notification
from app.email_transport import get_transport
from app.schemas import DispatchRequest, NotificationResponse, SendEmailRequest

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def _deliver(
    *,
    to: str,
    subject: str,
    html: str,
    template: str,
    triggered_by: str | None,
) -> NotificationResponse:
    """Send via the configured transport and log the outcome (sent or failed)."""
    try:
        message_id = await get_transport().send(to=to, subject=subject, html=html)
        logger.info("Email sent to={} subject={!r} resend_id={}", to, subject, message_id)
        return await notification_crud.log_sent(
            recipient=to,
            subject=subject,
            template=template,
            resend_id=message_id,
            triggered_by=triggered_by,
        )
    except Exception as exc:
        logger.error("Email send failed to={} error={}", to, exc)
        return await notification_crud.log_failed(
            recipient=to,
            subject=subject,
            template=template,
            error=str(exc),
            triggered_by=triggered_by,
        )


@router.post(
    "/send",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(can_send_notification)],
)
async def send_email(payload: SendEmailRequest) -> NotificationResponse:
    """
    Send an email via the configured transport and log the result.

    This is an internal endpoint — called by other services over the Docker
    network, protected by admin:notifications:write scope.
    """
    return await _deliver(
        to=payload.to,
        subject=payload.subject,
        html=payload.html,
        template=payload.template,
        triggered_by=payload.triggered_by,
    )


@router.post(
    "/dispatch",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(can_send_notification)],
)
async def dispatch_notification(payload: DispatchRequest) -> NotificationResponse:
    """
    Dispatch a notification by type. The service renders the email content
    (subject + html) based on the notification type and provided data.

    This is the preferred endpoint for other microservices to call.
    """
    subject, html = email_templates.render(payload.notification_type, payload.data, payload.locale)

    return await _deliver(
        to=payload.to,
        subject=subject,
        html=html,
        template=payload.notification_type.value,
        triggered_by=payload.triggered_by,
    )


@router.get(
    "/",
    response_model=list[NotificationResponse],
    dependencies=[Depends(can_read_notifications)],
)
async def list_notifications(
    page: int = 1,
    page_size: int = 20,
) -> list[NotificationResponse]:
    """List notification history. Admin only."""
    return await notification_crud.list_notifications(
        page=page,
        page_size=page_size,
    )
