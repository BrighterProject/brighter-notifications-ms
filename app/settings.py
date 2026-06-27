import os
from typing import Literal

db_url = os.environ.get("DB_URL", "sqlite://:memory:")

resend_api_key = os.environ.get("RESEND_API_KEY", "re_test_placeholder")
default_from_email = os.environ.get("DEFAULT_FROM_EMAIL", "Ploshtadka.BG <noreply@площадка.бг>")

frontend_base_url = os.environ.get("FRONTEND_BASE_URL", "http://localhost")

# Email delivery transport: "resend" (prod, HTTPS API) or "smtp" (dev/e2e → mailpit).
email_transport: Literal["resend", "smtp"] = (
    "smtp" if os.environ.get("EMAIL_TRANSPORT", "resend").lower() == "smtp" else "resend"
)
smtp_host = os.environ.get("SMTP_HOST", "mailpit")
smtp_port = int(os.environ.get("SMTP_PORT", "1025"))
smtp_starttls = os.environ.get("SMTP_STARTTLS", "false").lower() == "true"
