import os

db_url = os.environ.get("DB_URL", "sqlite://:memory:")

resend_api_key = os.environ.get("RESEND_API_KEY", "re_test_placeholder")
default_from_email = os.environ.get("DEFAULT_FROM_EMAIL", "Ploshtadka.BG <noreply@площадка.бг>")

frontend_base_url = os.environ.get("FRONTEND_BASE_URL", "http://localhost")
