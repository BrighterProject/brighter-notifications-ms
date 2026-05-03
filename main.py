from pathlib import Path

import resend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ms_core import setup_app

from app.logging import setup_logging
from app.settings import db_url, resend_api_key

TORTOISE_ORM = {
    "connections": {"default": db_url},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
            "migrations": "migrations.models",
        },
    },
}

setup_logging()

resend.api_key = resend_api_key

application = FastAPI(title="brighter-notifications-ms", redirect_slashes=False)

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_app(application, db_url, Path("app") / "routers", ["app.models"])
