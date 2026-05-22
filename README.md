# DjangoApi

A Django REST API for managing **patient records** with **JWT authentication** and automatic Django user provisioning when patients are created. The project demonstrates three different ways to expose the same domain logic: function-based views, a ViewSet with a router, and generic class-based views.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database setup](#database-setup)
- [Running the server](#running-the-server)
- [Docker deployment](#docker-deployment)
- [Authentication](#authentication)
- [Patient data model](#patient-data-model)
- [API overview](#api-overview)
- [API reference](#api-reference)
- [Example workflows](#example-workflows)
- [Architecture notes](#architecture-notes)
- [Development](#development)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Patient CRUD** (coverage depends on API version — see [API overview](#api-overview))
- **JWT auth** via Simple JWT (login, refresh, protected endpoints by default)
- **User registration** endpoint for explicit account creation
- **Automatic user provisioning** when creating a patient (v2 and v3): generates a unique username and links it to the patient record
- **Validation** for gender choices and local phone format (8 digits, starting with `8` or `9`)
- **Multiple API styles** (v1 function views, v2 ViewSet, v3 generics) for learning and comparison

---

## Tech stack

Pinned versions live in `requirements.txt`. Summary:

| Component | Version |
|-----------|---------|
| Python | 3.11+ recommended |
| Django | 6.0.5 |
| Django REST Framework | 3.17.1 |
| djangorestframework-simplejwt | 5.5.1 |
| django-environ | 0.13.0 |
| MySQL driver | mysqlclient 2.2.8 |

---

## Project structure

```
DjangoApi/
├── main/                 # Project settings, root URL routing, WSGI/ASGI
├── patients/             # Patient model, serializers, and API implementations
├── authenticator/        # Registration and user lookup views
├── utils/                # Shared helpers (e.g. patient create + user linking)
├── manage.py
├── requirements.txt      # Runtime Python dependencies
├── requirements-dev.txt  # Optional dev/typing dependencies
├── Dockerfile            # Application image
├── docker-compose.yml    # Web + MySQL stack
├── docker/entrypoint.sh  # DB wait, migrations, then start server
├── .env.example          # Environment variable template
├── .env.docker.example   # Env template tuned for Compose
└── README.md
```

---

## Prerequisites

1. **Python 3.11+** (or a version compatible with Django 6)
2. **MySQL** server reachable from your machine
3. **MySQL client libraries** for building `mysqlclient` (on macOS: Xcode CLI tools; on Linux: `default-libmysqlclient-dev` or equivalent)

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd DjangoApi
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Optional — typing stubs for IDE / mypy support:

```bash
pip install -r requirements-dev.txt
```

To regenerate pinned versions after upgrading packages locally:

```bash
pip install -r requirements.txt
pip freeze > requirements-lock.txt   # optional full lockfile for your platform
```

### 4. Environment file

Copy the example env file and edit it for your database:

```bash
cp .env.example .env
```

See [Configuration](#configuration).

### 5. Apply migrations

```bash
python manage.py makemigrations patients
python manage.py migrate
```

### 6. (Optional) Create a superuser

```bash
python manage.py createsuperuser
```

Use this account to obtain JWT tokens or access the Django admin after registering models there.

---

## Configuration

Settings are loaded from a `.env` file at the project root using **django-environ**.

### Environment variables

| Variable | Required | Description | Development | Production |
|----------|----------|-------------|-------------|------------|
| `DATABASE_URL` | Yes | MySQL connection URL | `mysql://user:pass@127.0.0.1:3306/django_api` | Same pattern, production credentials |
| `SECRET_KEY` | Yes | Django signing key; keep secret | Unique value in `.env` (not committed) | Strong random key; never reuse the dev key |
| `DEBUG` | Yes | Enables debug mode and extra error pages | `True` | `False` |
| `ALLOWED_HOSTS` | Yes | Comma-separated hostnames the app will serve | `localhost,127.0.0.1` | Your domain(s), e.g. `api.example.com` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | No | How long the **access** token works (default `60`) | `60` | Shorter in production if possible (e.g. `15–30`) |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | No | How long the **refresh** token works (default `7`) | `7` | `1–30` depending on security policy |

Copy the template and edit locally:

```bash
cp .env.example .env
```

`.env.example` (abbreviated):

```env
DATABASE_URL=mysql://username:password@host:port/database
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Production — uncomment and set on the server:
# DEBUG=False
# SECRET_KEY=<generate with get_random_secret_key>
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Generate a production `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

On production, also use HTTPS, restrict database access, and rotate secrets if they are ever exposed.

### Django / DRF defaults (in code)

- **Default authentication**: JWT (`JWTAuthentication`)
- **Default permission**: `IsAuthenticated` — most DRF endpoints require a valid Bearer token
- **Time zone**: UTC

---

## Database setup

1. Create an empty MySQL database, for example:

```sql
CREATE DATABASE django_api CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Point `DATABASE_URL` in `.env` at that database.

3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

The `patient` table is created from the `Patient` model (`db_table = 'patient'`).

---

## Running the server

```bash
python manage.py runserver
```

Default base URL: **http://127.0.0.1:8000/**

Interactive API browsing is not enabled by default; use `curl`, Postman, or similar tools.

---

## Docker deployment

Run the API and MySQL together with **Docker Compose**. The web container uses **Gunicorn**, waits for the database, runs migrations on startup, then serves the app on port **8000**.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) (Compose v2: `docker compose` CLI)

### Quick start (development)

1. **Create a `.env` file** for Compose (gitignored):

```bash
cp .env.docker.example .env
```

Generate a real `SECRET_KEY` and paste it into `.env`.

2. **Build and start** the stack:

```bash
docker compose up --build
```

3. **Open the API**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Run in the background:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f web
```

Stop and remove containers (keep database volume):

```bash
docker compose down
```

Stop and remove containers **and** the MySQL volume:

```bash
docker compose down -v
```

### How it works

```mermaid
flowchart TB
  Host[Host :8000] --> Web[web container\nGunicorn + Django]
  Web --> DB[(db container\nMySQL 8.4)]
  Web --> Env[.env + compose environment]
```

| Service | Image / build | Role |
|---------|----------------|------|
| `db` | `mysql:8.4` | Database `django_db`, user `django` / password `django` |
| `web` | `Dockerfile` | Django app; `DATABASE_URL` points at host `db` |

`docker-compose.yml` sets:

```env
DATABASE_URL=mysql://django:django@db:3306/django_db
```

That overrides `DATABASE_URL` in `.env` so the app reaches MySQL on the internal Docker network (hostname `db`, not `127.0.0.1`).

The entrypoint script (`docker/entrypoint.sh`) waits until Django can connect, runs `makemigrations` and `migrate`, then starts Gunicorn.

### Useful Docker commands

```bash
# Rebuild after code or dependency changes
docker compose up --build -d

# Run Django management commands
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Open a shell inside the web container
docker compose exec web sh
```

### Production-style Compose

Use the production override file (sets `DEBUG=False`, does not add dev-only options):

```bash
cp .env.docker.example .env
# Edit .env: DEBUG=False, strong SECRET_KEY, real ALLOWED_HOSTS

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Unique dev key | Strong random key; never commit |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Your public domain(s) |
| MySQL port on host | Commented out (not exposed) | Keep commented out |
| HTTPS | Optional locally | Terminate TLS at a reverse proxy (nginx, Traefik, cloud LB) |

**Production checklist**

1. Set `DEBUG=False` and production `ALLOWED_HOSTS` in `.env`.
2. Use a new `SECRET_KEY` (see [Configuration](#configuration)).
3. Change MySQL passwords in `docker-compose.yml` / use Docker secrets or an external managed database.
4. Put a reverse proxy in front of Gunicorn for HTTPS.
5. Do not commit `.env` or publish port `3306` unless required.
6. Consider external MySQL (RDS, Cloud SQL) and set `DATABASE_URL` accordingly; you can run only the `web` service or remove the `db` service from Compose.

### Connect to MySQL from your host (optional)

In `docker-compose.yml`, uncomment under `db`:

```yaml
ports:
  - "3306:3306"
```

Then connect with any client using `127.0.0.1:3306`, user `django`, password `django`, database `django_db`.

### Troubleshooting (Docker)

| Problem | What to try |
|---------|-------------|
| `web` exits immediately | `docker compose logs web` — often missing `.env` or invalid `SECRET_KEY` |
| Database connection errors | Ensure `db` is healthy: `docker compose ps`; wait for healthcheck |
| `ALLOWED_HOSTS` error when `DEBUG=False` | Add your domain or `localhost` to `ALLOWED_HOSTS` in `.env` |
| Port 8000 in use | Change mapping to `"8080:8000"` under `web.ports` |
| Stale schema | `docker compose exec web python manage.py migrate` |
| Rebuild from scratch | `docker compose down -v && docker compose up --build` |

---

## Authentication

### Register a user

**`POST /api/auth/register/`**

No authentication required for this endpoint (it uses `CreateAPIView` without overriding global permissions on the class — verify behavior if you add global `IsAuthenticated` to all views).

Request body:

```json
{
  "username": "jane.doe",
  "password": "your-secure-password"
}
```

Success (`201`):

```json
{
  "message": "User created successfully"
}
```

### Obtain JWT tokens (login)

**`POST /api/auth/login/`**

```json
{
  "username": "jane.doe",
  "password": "your-secure-password"
}
```

Response (`200`):

```json
{
  "access": "<access-token>",
  "refresh": "<refresh-token>"
}
```

### Refresh access token

**`POST /api/auth/refresh/`**

```json
{
  "refresh": "<refresh-token>"
}
```

### Token lifetimes

This project uses [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/) with two tokens:

| Token | Purpose | Default (before `.env`) | Configured via |
|-------|---------|-------------------------|----------------|
| **access** | Sent as `Authorization: Bearer …` on API calls | 5 minutes | `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` |
| **refresh** | Used only at `/api/auth/refresh/` to get a new access token | 1 day | `JWT_REFRESH_TOKEN_LIFETIME_DAYS` |

Extend lifetimes in `.env` (then restart the server or rebuild Docker):

```env
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=120
JWT_REFRESH_TOKEN_LIFETIME_DAYS=30
```

Settings mapping in `main/settings.py`:

```python
SIMPLE_JWT = {
  "ACCESS_TOKEN_LIFETIME": timedelta(minutes=...),
  "REFRESH_TOKEN_LIFETIME": timedelta(days=...),
}
```

**Notes:**

- Only the **access** token is sent on patient/auth API calls. When it expires, call **`POST /api/auth/refresh/`** with the refresh token — you do not need to log in again until the refresh token expires.
- Longer access tokens are simpler for clients but less secure if leaked. Prefer a shorter access token plus refresh (e.g. 15–60 min access, 7–30 days refresh).
- Existing tokens keep their original expiry until you log in again and get new ones.
- For Docker: `docker compose up --build -d` after changing `.env`.

Other `SIMPLE_JWT` options (rotation, blacklist) are documented in the [Simple JWT settings](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html) guide.

### Use tokens on protected requests

Add the header to patient and other protected routes:

```
Authorization: Bearer <access-token>
```

### Current user profile

**`GET /api/auth/me/`**

Requires a valid JWT. Returns the **authenticated** user (from the token), not a username in the URL.

Example response:

```json
{
  "id": 1,
  "username": "jane.doe",
  "email": "",
  "first_name": "",
  "last_name": "",
  "is_active": true,
  "date_joined": "2026-05-21T14:10:54.413358Z",
  "last_login": "2026-05-21T15:00:00.123456Z"
}
```

If the user has no linked patient record, `patient` is `null`.

---

## Patient data model

| Field | Type | Notes |
|-------|------|--------|
| `id` | integer | Primary key (read-only in API) |
| `user` | FK → `User` | Optional; set on create in v2/v3 via `perform_create` |
| `first_name` | string | max 128 |
| `last_name` | string | max 128 |
| `date_of_birth` | date | ISO 8601 (`YYYY-MM-DD`) |
| `gender` | choice | `M` (Male) or `F` (Female); stored uppercase |
| `phone_number` | string | 8 digits, unique, must match `^[89]\d{7}$` |
| `address` | string | max 128 |
| `medical_history` | text | free text |
| `created_at` | datetime | set on create (read-only) |
| `updated_at` | datetime | auto-updated (read-only) |

### Example create payload

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "date_of_birth": "1990-05-15",
  "gender": "m",
  "phone_number": "91234567",
  "address": "123 Main St",
  "medical_history": "No known allergies."
}
```

`gender` may be sent in any case; it is normalized to uppercase before save.

---

## API overview

The same **Patient** resource is exposed under three versioned styles:

| Version | Base path | Style | Auth on patient routes |
|---------|-----------|--------|-------------------------|
| **v1** | `/api/v1/patient/` | Function-based `@api_view` | Subject to global DRF defaults when using `@api_view` |
| **v2** | `/api/v2/patient/` | `ModelViewSet` + router | `IsAuthenticated` on ViewSet |
| **v3** | `/api/v3/patient/` | Generic `ListCreateAPIView` / `RetrieveAPIView` | `IsAuthenticated` |

**Create behavior differs by version:**

- **v2 / v3**: Shared `perform_create` creates a Django `User` and **links** it to the patient (`user` FK populated).
- **v1**: Creates a Django `User` with a generated username but **does not** attach that user to the patient record on save (implementation gap).

---

## API reference

### Auth

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/register/` | Register username/password |
| `POST` | `/api/auth/login/` | Obtain access + refresh JWT |
| `POST` | `/api/auth/refresh/` | Refresh access token |
| `GET` | `/api/auth/me/` | Current user profile + linked patient (JWT required) |

---

### Patients — v1 (function-based)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/patient/` | List all patients |
| `POST` | `/api/v1/patient/` | Create patient (+ orphan user account) |
| `GET` | `/api/v1/patient/<id>/` | Get one patient |
| `PUT` | `/api/v1/patient/<id>/` | Update patient |

**Responses:** list/create often use `JsonResponse`; detail/update use DRF `Response`.

---

### Patients — v2 (ViewSet)

Router prefix: `/api/v2/`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v2/patient/` | List |
| `POST` | `/api/v2/patient/` | Create (with linked user) |
| `GET` | `/api/v2/patient/<id>/` | Retrieve |
| `PUT` | `/api/v2/patient/<id>/` | Full update |
| `PATCH` | `/api/v2/patient/<id>/` | Partial update |
| `DELETE` | `/api/v2/patient/<id>/` | Delete |

---

### Patients — v3 (generic views)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v3/patient/` | List |
| `POST` | `/api/v3/patient/` | Create (with linked user) |
| `GET` | `/api/v3/patient/<id>/` | Retrieve by `id` |

v3 does not expose update or delete on the generic retrieve route.

---

### Common HTTP status codes

| Code | Meaning |
|------|---------|
| `200` | Success (GET, PUT) |
| `201` | Created (POST) |
| `400` | Validation error or registration failure |
| `401` | Missing or invalid JWT |
| `404` | Patient not found |

---

## Example workflows

### 1. Register, login, and create a patient (v2)

```bash
# Register
curl -s -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"api.user","password":"SecurePass123!"}'

# Login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"api.user","password":"SecurePass123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# Create patient
curl -s -X POST http://127.0.0.1:8000/api/v2/patient/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "first_name": "Ada",
    "last_name": "Lovelace",
    "date_of_birth": "1815-12-10",
    "gender": "F",
    "phone_number": "87654321",
    "address": "London",
    "medical_history": "Historical figure."
  }'
```

### 2. List patients (v1)

```bash
curl -s http://127.0.0.1:8000/api/v1/patient/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Refresh an expired access token

```bash
curl -s -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<your-refresh-token>"}'
```

---

## Architecture notes

```mermaid
flowchart LR
  Client -->|JWT| Auth[Auth endpoints]
  Client -->|JWT| V1[v1 Function views]
  Client -->|JWT| V2[v2 ViewSet]
  Client -->|JWT| V3[v3 Generic views]
  V2 --> Utils[perform_create]
  V3 --> Utils
  Utils --> User[(Django User)]
  Utils --> Patient[(Patient)]
  V1 --> Patient
  V1 --> User
```

- **Serializers** validate and normalize input (e.g. gender casing).
- **`perform_create`** (v2/v3) centralizes username generation: `{first}.{last}.{microsecond+salt}` in lowercase, then `serializer.save(user=user)`.
- **v1** duplicates similar username logic inline but does not pass `user` into `save()`.

---

## Development

### Useful commands

```bash
# Check configuration
python manage.py check

# Create migrations after model changes
python manage.py makemigrations patients

# Apply migrations
python manage.py migrate

# Django shell
python manage.py shell

# Run tests (placeholder — add tests under patients/ and authenticator/)
python manage.py test
```

### Adding `rest_framework` to installed apps

If you see import or schema errors related to DRF, ensure `rest_framework` is listed in `INSTALLED_APPS` in project settings alongside `patients` and `authenticator`.

### Code style

The codebase uses 2-space indentation in several modules; match surrounding style when contributing.

---

## Known limitations

1. **Migrations** may need to be generated on first clone (`makemigrations` for `patients`).
2. **v1 create** does not link the auto-created `User` to the `Patient` record.
3. **Auto-provisioned users** (on patient create) have no password set via `create_user(username=...)` only — they cannot log in until a password is set unless you extend the flow.
4. **v1 response inconsistency** — mix of `JsonResponse` and DRF `Response`.
5. **Phone format** is region-specific (8-digit, leading 8 or 9); not E.164 international.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `mysqlclient` install fails | Install OS MySQL dev headers; then `pip install -r requirements.txt` inside the venv |
| `django.db.utils.OperationalError` | Verify MySQL is running, database exists, and `DATABASE_URL` is correct |
| `401 Unauthorized` | Login again; send `Authorization: Bearer <access>`; refresh if access expired |
| Phone validation error | Use exactly 8 digits starting with `8` or `9` |
| Unique phone constraint | Use a new `phone_number` or delete the existing row |
| Import errors for DRF | `pip install -r requirements.txt` and add `rest_framework` to `INSTALLED_APPS` |

---

## License

Specify your license here (e.g. MIT, Apache 2.0) or mark the project as private/internal.
