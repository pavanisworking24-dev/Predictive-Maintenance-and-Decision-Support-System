# Backend

FastAPI backend for the **Predictive Maintenance and Decision Support System**.

## 1. Technology Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic Settings
- SQLAlchemy 2.x
- PostgreSQL
- Psycopg 3
- Alembic
- pgvector
- Pytest
- HTTPX
- JSON Schema
- Docker

## 2. Project Structure

```text
backend/
├── alembic.ini
├── Dockerfile
├── requirements.txt
├── README.md
├── migrations/
│   ├── env.py
│   ├── README
│   └── versions/
├── app/
│   ├── api/
│   │   └── health.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── alert.py
│   │   ├── chat_message.py
│   │   ├── chat_session.py
│   │   ├── explanation.py
│   │   ├── knowledge_chunk.py
│   │   ├── knowledge_document.py
│   │   ├── machine.py
│   │   ├── maintenance_record.py
│   │   ├── model_version.py
│   │   ├── prediction.py
│   │   ├── risk_score.py
│   │   ├── risk_threshold_config.py
│   │   ├── sensor_reading.py
│   │   └── user.py
│   ├── main.py
│   └── tests/
└── tests/
    ├── conftest.py
    ├── test_database.py
    └── test_main.py
```

The repository-level `tests/` directory contains project contract tests.

## 3. Local Setup

### Prerequisites

- Python 3.12
- Git
- Docker Desktop
- PostgreSQL through Docker Compose

### Create a virtual environment

Run from the repository root:

```powershell
py -3.12 -m venv backend/.venv
```

Activate it:

```powershell
.\backend\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r backend/requirements.txt
```

## 4. Environment Configuration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Configure application settings and database URLs in the root `.env` file.

Example:

```env
ENVIRONMENT=development
DEBUG=false
DATABASE_URL=postgresql+psycopg://pm_user:YOUR_PASSWORD@127.0.0.1:5433/predictive_maintenance
TEST_DATABASE_URL=postgresql+psycopg://pm_user:YOUR_PASSWORD@127.0.0.1:5433/predictive_maintenance_test
```

Use your actual local credentials. Never commit `.env` or database credentials to Git.

Allowed environment values:

- `development`
- `testing`
- `production`

## 5. Database Setup

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

The PostgreSQL service is exposed on host port `5433` and listens internally on port `5432`.

The initial database schema is maintained in:

`docs/database/database-schema-v0.sql`

Optional seed data is maintained in:

`docs/database/seed-v0.sql`

The detailed database setup guide is:

`docs/database/database-setup-documentation.md`

## 6. SQLAlchemy and Database Sessions

Database configuration is maintained in:

- `app/core/config.py`
- `app/db/base.py`
- `app/db/session.py`

SQLAlchemy models are maintained in `app/models/`.

The project currently registers 14 application tables in SQLAlchemy metadata.

The application uses `SessionLocal` to create database sessions. The `get_db()` dependency provides request-scoped sessions and closes them after use.

## 7. Database Migrations

Alembic configuration is maintained in:

- `alembic.ini`
- `migrations/env.py`
- `migrations/versions/`

Run commands from the repository root.

Check migration status:

```powershell
python -m alembic -c backend/alembic.ini current
```

Check model and database metadata differences:

```powershell
python -m alembic -c backend/alembic.ini check
```

Generate a migration:

```powershell
python -m alembic -c backend/alembic.ini revision --autogenerate -m "describe schema change"
```

Apply migrations:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

Review every generated migration before applying it.

**Important:** The current baseline migration is empty because the initial schema was created using the SQL schema file. It records the starting migration revision; it does not create the initial database tables.

## 8. Run the Backend Locally

From the repository root:

```powershell
uvicorn app.main:app --app-dir backend --reload
```

The backend will be available at:

- Root: http://localhost:8000/
- Health: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs

## 9. Run Using Docker

Build the backend image:

```powershell
docker compose build backend
```

Start the backend:

```powershell
docker compose up -d backend
```

Check container status:

```powershell
docker compose ps
```

View backend logs:

```powershell
docker compose logs backend
```

The Docker backend is available at:

- Root: http://localhost:8001/
- Health: http://localhost:8001/health
- Swagger UI: http://localhost:8001/docs

The host port is 8001 because port 8000 is already occupied on the development machine. The container listens internally on port 8000.

Start the full application stack:

```powershell
docker compose up -d
```

## 10. Run Tests

Run API tests:

```powershell
python -m pytest backend/tests/test_main.py -v
```

Run database integration tests:

```powershell
python -m pytest backend/tests/test_database.py -v
```

Run project contract tests:

```powershell
python -m pytest tests/contracts -v
```

Run the complete test suite:

```powershell
python -m pytest -v
```

Database integration tests use a separate PostgreSQL database configured through `TEST_DATABASE_URL`.

Tests use transaction rollback to isolate database changes.

Never point the test configuration at the development or production database.

## 11. Current Backend Features

- FastAPI application setup
- Root and health endpoints
- Centralized application logging
- HTTP error handling
- Request validation error handling
- Unexpected server error handling
- Environment-based configuration
- PostgreSQL database connectivity
- SQLAlchemy ORM integration
- Fourteen registered database models
- Database session management
- Alembic migration configuration
- Database integration tests
- Docker support

## 12. Development Status

The initial backend foundation and database integration layer are implemented.

Subsequent backend work includes authentication, role-based access control, machine APIs, prediction APIs, alert management, ML service integration, and RAG integration.

The current health endpoint does not independently verify PostgreSQL connectivity.