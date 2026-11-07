# Smart Tag Hub

A backend and admin panel for managing URLs used by NFC tags. Write a short URL to a tag once and update its destination whenever needed.

*Leia em português: [ReadMe-PTBR.md](ReadMe-PTBR.md)*

## Implemented features

- Short links with random or custom slugs.
- Link listing and search.
- Destination updates.
- Activation and deactivation without deleting records.
- Temporary (`307`) public redirects at `/r/{slug}`.
- Backward compatibility with legacy `/{slug}` URLs.
- Friendly public error pages.
- Responsive admin panel served by FastAPI.
- Single-admin authentication with Argon2, signed sessions, CSRF protection, and login throttling.
- Session-protected management API.
- SQLite for development and PostgreSQL support for production.
- Alembic migrations, health check, Dockerfile, and CI with tests and Ruff.

The current scope is intentionally **single-admin**. Customer accounts, per-user ownership, and analytics are future enhancements.

## Tech stack

- Python 3.11+
- FastAPI, Starlette, and Jinja2
- Async SQLAlchemy
- SQLite/aiosqlite and PostgreSQL/asyncpg
- Alembic
- Pytest, HTTPX, and Ruff
- Uvicorn and Docker

## Architecture

| Layer | Responsibility |
| --- | --- |
| `api/` | Public routes, management API, admin panel, authentication, templates, and settings. |
| `domain/` | Entity, business rules, validation, and repository contract. |
| `infrastructure/` | Database, ORM model, and SQLAlchemy repository. |
| `migrations/` | Versioned schema changes with Alembic. |
| `tests/` | Unit and integration tests using in-memory SQLite. |
| `docs/` | Operational documentation and conceptual diagrams. |

The domain is independent from storage. Both the API and the admin panel use the same `LinkService`.

## Running locally

### 1. Install

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
```

### 2. Configure the administrator

Copy `.env.example` to `.env`, then generate a session secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set it as `SECRET_KEY`. Generate an Argon2 password hash without storing the plain password:

```bash
python -m scripts.generate_password_hash
```

Set the generated value as `ADMIN_PASSWORD_HASH` in `.env`, enclosed in single quotes.

### 3. Migrate and start

```bash
alembic upgrade head
pytest
uvicorn api.main:app --reload
```

Available URLs:

- Admin: `http://localhost:8000/admin`
- Development API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/_health`
- URL to write to an NFC tag: `http://localhost:8000/r/{slug}`

Use your final HTTPS domain when writing production tags.

### Databases created before Alembic

If an old database already has the `links` table but no `alembic_version` table, mark the baseline before upgrading:

```bash
alembic stamp 0001
alembic upgrade head
```

Back up the database first. New databases only need `alembic upgrade head`.

## Management API

These routes require the session created by the admin login. The original `POST /links` remains available as a creation alias; the other management endpoints use `/api/links`:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/links?q=` | List and filter links. |
| `POST` | `/api/links` | Create a link. |
| `GET` | `/api/links/{slug}` | Get a link. |
| `PATCH` | `/api/links/{slug}` | Update `target_url` and/or `is_active`. |

## Quality checks

```bash
pytest -q
ruff check .
ruff format --check .
pip-audit
```

The CI workflow runs these checks with Python 3.12 on pushes to `main` and Pull Requests.

## Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) for production settings, PostgreSQL, migrations, HTTPS, backups, and the launch checklist. The Dockerfile is provider-independent.

## Author

Renan Barbosa — [GitHub](https://github.com/renanbarbosaaa)
