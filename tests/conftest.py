"""
Shared pytest fixtures available to every test file automatically.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.mjml_renderer import warm_template_cache
from main import application

from .factories import make_admin, make_user


@pytest.fixture(scope="session", autouse=True)
def _warm_mjml_cache():
    warm_template_cache()


def _inject_user_headers(user: dict) -> dict[str, str]:
    return {
        "X-User-Id": user["id"],
        "X-Username": user["username"],
        "X-User-Scopes": user["scopes"],
    }


@pytest.fixture
def admin_client():
    """Async client factory with admin headers."""

    async def _make():
        user = make_admin()
        transport = ASGITransport(app=application)
        return AsyncClient(
            transport=transport,
            base_url="http://test",
            headers=_inject_user_headers(user),
        )

    return _make


@pytest.fixture
def anon_app():
    """Async client with no auth headers — for 401/403/422 tests."""

    async def _make():
        transport = ASGITransport(app=application)
        return AsyncClient(transport=transport, base_url="http://test")

    return _make


@pytest.fixture
def client_factory():
    """Build a client with arbitrary user headers."""

    async def _make(user: dict | None = None):
        user = user or make_user()
        transport = ASGITransport(app=application)
        return AsyncClient(
            transport=transport,
            base_url="http://test",
            headers=_inject_user_headers(user),
        )

    return _make
