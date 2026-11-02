from app.core.exceptions import register_exception_handlers
from app.main import app
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

# Client for testing the actual backend
client = TestClient(app)


# Separate application for testing error handlers
error_test_app = FastAPI()

register_exception_handlers(error_test_app)


class SampleRequest(BaseModel):
    name: str


# Temporary endpoint for testing validation errors
@error_test_app.post("/test-validation")
def validation_endpoint(data: SampleRequest):
    return {"name": data.name}


# Temporary endpoint for testing internal server errors
@error_test_app.get("/test-error")
def error_endpoint():
    raise RuntimeError("This is a test internal error")


error_client = TestClient(error_test_app, raise_server_exceptions=False)


# Test 1: Root endpoint
def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Predictive Maintenance Backend is running"}


# Test 2: Health endpoint
def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "backend"}


# Test 3: Invalid route
def test_invalid_route():
    response = client.get("/invalid-route")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "NOT_FOUND"
    assert data["message"] == "Not Found"
    assert data["details"] is None


# Test 4: Validation error
def test_validation_error():
    response = error_client.post("/test-validation", json={})

    assert response.status_code == 422

    data = response.json()

    assert data["error"] == "VALIDATION_ERROR"
    assert data["message"] == "Request validation failed"
    assert "issues" in data["details"]


# Test 5: Internal server error
def test_internal_server_error():
    response = error_client.get("/test-error")

    assert response.status_code == 500

    data = response.json()

    assert data["error"] == "INTERNAL_SERVER_ERROR"
    assert data["message"] == "An unexpected server error occurred"

    assert "This is a test internal error" not in response.text
