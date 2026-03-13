# CLAUDE.md — brighter-notifications-ms

FastAPI microservice for sending emails via Resend (part of the BrighterProject platform).

## Package management

Always use `uv`. Never use `pip` directly.

```bash
uv add <package>       # add dependency
uv sync                # install from lockfile
uv run <command>       # run in the venv
```

## Running

```bash
uv run pytest                                                        # run tests
uv run uvicorn main:application --host 0.0.0.0 --port 8004          # dev server
```

## Architecture

### Technology Stack

- **API Framework**: FastAPI with Uvicorn (port 8004)
- **Database**: PostgreSQL with Tortoise ORM and Aerich migrations
- **Email provider**: Resend (via `resend` Python SDK)
- **Testing**: pytest with AsyncMock-based CRUD mocking (no real DB or Resend calls in tests)

## Auth architecture — critical

Auth is delegated entirely to Traefik via `forwardAuth`. JWT validation happens at the gateway. This service only reads the headers Traefik injects after a successful check:

| Header          | Type   | Description                        |
|-----------------|--------|------------------------------------|
| `X-User-Id`     | UUID   | Authenticated user's ID            |
| `X-Username`    | string | Authenticated user's username      |
| `X-User-Scopes` | string | Space-separated list of scopes     |

`get_current_user()` in `app/deps.py` reads these headers — it does not validate any token itself. **Do not add JWT validation middleware inside this service.**

## Email sending

This is an **internal service** — other microservices call `POST /notifications/send` over the Docker network to send emails. It uses Resend's Python SDK directly (no SMTP relay or mail server needed).

### How other services call it

```python
# From bookings-ms, payments-ms, etc.
resp = await httpx_client.post(
    "http://notifications-ms:8004/notifications/send",
    json={
        "to": "user@example.com",
        "subject": "Booking Confirmed",
        "html": "<h1>Your booking is confirmed!</h1>",
        "template": "booking_confirmed",
        "triggered_by": "bookings-ms",
    },
    headers=system_admin_headers,  # needs admin:notifications:write
)
```

## Project structure

```
app/
  settings.py          # DB_URL, RESEND_API_KEY, DEFAULT_FROM_EMAIL
  models.py            # Tortoise ORM model: Notification
  schemas.py           # Pydantic: NotificationResponse, SendEmailRequest
  crud.py              # NotificationCRUD — logs sent/failed emails
  deps.py              # Auth deps, scope checkers
  scopes.py            # NotificationScope StrEnum
  routers/
    notifications.py   # /notifications endpoints
    health.py          # /health/live, /health/ready
tests/
  conftest.py          # Fixtures: admin_client, anon_app, client_factory
  factories.py         # make_user(), make_admin(), notification_response()
  test_notifications.py
  test_scopes.py
```

## Scopes

| Scope                        | Who has it  | Purpose                           |
|------------------------------|-------------|-----------------------------------|
| `admin:notifications`        | Admin       | Super-scope                       |
| `admin:notifications:read`   | Admin       | View notification history          |
| `admin:notifications:write`  | Admin       | Send notifications (internal)      |

## Endpoints

| Method | Path                    | Scopes                       | Notes                        |
|--------|-------------------------|------------------------------|------------------------------|
| POST   | `/notifications/send`   | `admin:notifications:write`  | Send email via Resend        |
| GET    | `/notifications/`       | `admin:notifications:read`   | List notification history    |
| GET    | `/health/live`          | none                         | Liveness probe               |
| GET    | `/health/ready`         | none                         | Readiness probe (DB check)   |

## Environment variables

| Variable             | Default                                      | Description                    |
|----------------------|----------------------------------------------|--------------------------------|
| `DB_URL`             | `sqlite://:memory:`                          | Database connection string     |
| `RESEND_API_KEY`     | `re_test_placeholder`                        | Resend API key                 |
| `DEFAULT_FROM_EMAIL` | `Brighter.BG <noreply@brighter.bg>`      | Sender address                 |
| `FRONTEND_BASE_URL`  | `http://localhost`                           | Frontend URL for email links   |

## Testing conventions

- **Mock the CRUD layer** with `AsyncMock` (`patch("app.routers.notifications.notification_crud")`)
- **Mock `resend`** via `patch("app.routers.notifications.resend")`
- Use `anon_app` for real scope/auth dep checks (422 assertions on missing headers)

## Database

- Tests: SQLite in-memory (default, mocked via CRUD patch)
- Production: PostgreSQL (`DB_URL` env var)
- Migrations: Aerich

```bash
uv run aerich migrate --name <description>
uv run aerich upgrade
```
