# Backend

FastAPI backend for the **Predictive Maintenance and Decision Support System**.

## 1. Technology Stack

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic Settings
- Pytest
- HTTPX
- JSON Schema
- Docker

## 2. Project Structure

```text
backend/
├── Dockerfile
├── requirements.txt
├── README.md
├── app/
│   ├── api/
│   │   └── health.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   └── main.py
└── tests/
    └── test_main.py
```

## 3. Local Setup

### Prerequisites

- Python 3.12
- Git
- Visual Studio Code

### Create a virtual environment

Run these commands from the project root:

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

Configure the application settings in `.env`:

```env
ENVIRONMENT=development
DEBUG=false
```

Keep your database credentials in `.env`. Never commit this file to Git.

Allowed environment values:

- `development`
- `testing`
- `production`

## 5. Run the Backend Locally

From the project root:

```powershell
uvicorn app.main:app --app-dir backend --reload
```

The backend will be available at:

- Root: http://localhost:8000/
- Health: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs

## 6. Run Using Docker

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

Start the full application stack, including PostgreSQL, using:

```powershell
docker compose up -d
```

## 7. Run Tests

Run backend application tests:

```powershell
python -m pytest backend/tests/test_main.py -v
```

Run project contract tests:

```powershell
python -m pytest tests/contracts -v
```

Run all tests:

```powershell
python -m pytest -v
```

## 8. Current Backend Features

- FastAPI application setup
- Root and health endpoints
- Centralized application logging
- HTTP error handling
- Request validation error handling
- Unexpected server error handling
- Environment-based application configuration
- Automated API tests
- Docker support

## 9. Development Status

The initial backend foundation is implemented.

Database integration, authentication, role-based access control, machine APIs, prediction APIs, alert management, and RAG integration are planned for subsequent backend milestones.

The current health endpoint does not verify PostgreSQL connectivity.