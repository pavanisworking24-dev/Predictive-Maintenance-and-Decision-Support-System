"""API tests for /api/v1/auth and /api/v1/users against the test database."""

import uuid
from datetime import timedelta

import pytest
from app.core.security import create_access_token, hash_password
from app.db.session import get_db
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient

PASSWORD = "Sup3r" + "-Secret-" + "Pass"


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def make_user(db_session, role="MAINTENANCE_ENGINEER", is_active=True, password=PASSWORD):
    user = User(
        id=uuid.uuid4(),
        name=f"Test {role}",
        email=f"test-{uuid.uuid4().hex[:10]}@example.com",
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db_session.add(user)
    db_session.flush()
    return user


def auth_header(user):
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def unique_email():
    return f"new-{uuid.uuid4().hex[:10]}@example.com"


# --- register ---------------------------------------------------------------
def test_register_creates_maintenance_engineer(client, db_session):
    email = unique_email()
    response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": PASSWORD, "name": "Ada"}
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "name", "role", "is_active"}
    assert body["role"] == "MAINTENANCE_ENGINEER"
    assert body["is_active"] is True

    stored = db_session.get(User, uuid.UUID(body["id"]))
    assert stored.password_hash.startswith("$argon2id$")
    assert stored.password_hash != PASSWORD


def test_register_rejects_client_supplied_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email(), "password": PASSWORD, "name": "Eve", "role": "ADMIN"},
    )

    assert response.status_code == 422


def test_register_duplicate_email_returns_400(client, db_session):
    existing = make_user(db_session)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": existing.email.upper(), "password": PASSWORD, "name": "Dup"},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "BAD_REQUEST"


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/v1/auth/register", json={"email": unique_email(), "password": "short", "name": "X"}
    )

    assert response.status_code == 422


# --- login ------------------------------------------------------------------
def test_login_returns_bearer_token_with_role(client, db_session):
    user = make_user(db_session, role="MAINTENANCE_MANAGER")
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": PASSWORD})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    me = client.get("/api/v1/users", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 403  # valid token, but not ADMIN


def test_login_wrong_password_returns_401(client, db_session):
    user = make_user(db_session)
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": unique_email(), "password": PASSWORD}
    )

    assert response.status_code == 401


def test_login_inactive_user_returns_401(client, db_session):
    user = make_user(db_session, is_active=False)
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": PASSWORD})

    assert response.status_code == 401


def test_register_then_login_flow(client):
    email = unique_email()
    client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD, "name": "N"})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["access_token"]


# --- token validation / logout -----------------------------------------------
def test_logout_requires_token(client):
    assert client.post("/api/v1/auth/logout").status_code == 401


def test_logout_with_valid_token(client, db_session):
    user = make_user(db_session)
    response = client.post("/api/v1/auth/logout", headers=auth_header(user))

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}


def test_expired_token_is_rejected(client, db_session):
    user = make_user(db_session, role="ADMIN")
    token = create_access_token({"sub": str(user.id), "role": "ADMIN"}, timedelta(seconds=-5))
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_garbage_token_is_rejected(client):
    response = client.get("/api/v1/users", headers={"Authorization": "Bearer not.a.jwt"})

    assert response.status_code == 401


def test_token_for_deleted_user_is_rejected(client):
    token = create_access_token({"sub": str(uuid.uuid4()), "role": "ADMIN"})
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_token_for_deactivated_user_is_rejected(client, db_session):
    user = make_user(db_session, role="ADMIN", is_active=False)

    assert client.get("/api/v1/users", headers=auth_header(user)).status_code == 401


def test_role_claim_in_token_is_not_trusted(client, db_session):
    engineer = make_user(db_session)
    token = create_access_token({"sub": str(engineer.id), "role": "ADMIN"})
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403


# --- RBAC: users --------------------------------------------------------------
def test_list_users_requires_authentication(client):
    assert client.get("/api/v1/users").status_code == 401


@pytest.mark.parametrize("role", ["MAINTENANCE_MANAGER", "MAINTENANCE_ENGINEER"])
def test_list_users_forbidden_for_non_admin(client, db_session, role):
    user = make_user(db_session, role=role)
    response = client.get("/api/v1/users", headers=auth_header(user))

    assert response.status_code == 403
    assert response.json()["error"] == "FORBIDDEN"


def test_admin_can_list_users(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    engineer = make_user(db_session)
    response = client.get("/api/v1/users?limit=100", headers=auth_header(admin))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    emails = {item["email"] for item in body["items"]}
    assert {admin.email, engineer.email} <= emails
    assert all("password_hash" not in item for item in body["items"])


def test_admin_can_filter_users_by_role(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    make_user(db_session, role="MAINTENANCE_MANAGER")
    response = client.get(
        "/api/v1/users?role=MAINTENANCE_MANAGER&limit=100", headers=auth_header(admin)
    )

    assert response.status_code == 200
    assert {item["role"] for item in response.json()["items"]} == {"MAINTENANCE_MANAGER"}


def test_admin_can_update_role(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role",
        json={"role": "MAINTENANCE_MANAGER"},
        headers=auth_header(admin),
    )

    assert response.status_code == 200
    assert response.json()["role"] == "MAINTENANCE_MANAGER"
    db_session.refresh(engineer)
    assert engineer.role == "MAINTENANCE_MANAGER"


def test_non_admin_cannot_update_role(client, db_session):
    manager = make_user(db_session, role="MAINTENANCE_MANAGER")
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role", json={"role": "ADMIN"}, headers=auth_header(manager)
    )

    assert response.status_code == 403


def test_engineer_cannot_promote_self(client, db_session):
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role", json={"role": "ADMIN"}, headers=auth_header(engineer)
    )

    assert response.status_code == 403


def test_update_role_unknown_user_returns_404(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    response = client.patch(
        f"/api/v1/users/{uuid.uuid4()}/role", json={"role": "ADMIN"}, headers=auth_header(admin)
    )

    assert response.status_code == 404


def test_update_role_rejects_invalid_role(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role", json={"role": "PILOT"}, headers=auth_header(admin)
    )

    assert response.status_code == 422


def test_admin_cannot_demote_self(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    response = client.patch(
        f"/api/v1/users/{admin.id}/role",
        json={"role": "MAINTENANCE_ENGINEER"},
        headers=auth_header(admin),
    )

    assert response.status_code == 400
"""API tests for /api/v1/auth and /api/v1/users against the test database."""


import pytest

PASSWORD = "Sup3r-Secret-Pass"


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


def make_user(db_session, role="MAINTENANCE_ENGINEER", is_active=True, password=PASSWORD):
    user = User(
        id=uuid.uuid4(),
        name=f"Test {role}",
        email=f"test-{uuid.uuid4().hex[:10]}@example.com",
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db_session.add(user)
    db_session.flush()
    return user


def auth_header(user):
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def unique_email():
    return f"new-{uuid.uuid4().hex[:10]}@example.com"


# --- register ---------------------------------------------------------------
def test_register_creates_maintenance_engineer(client, db_session):
    email = unique_email()
    response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": PASSWORD, "name": "Ada"}
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "email", "name", "role", "is_active"}
    assert body["role"] == "MAINTENANCE_ENGINEER"
    assert body["is_active"] is True

    stored = db_session.get(User, uuid.UUID(body["id"]))
    assert stored.password_hash.startswith("$argon2id$")
    assert stored.password_hash != PASSWORD


def test_register_rejects_client_supplied_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email(), "password": PASSWORD, "name": "Eve", "role": "ADMIN"},
    )

    assert response.status_code == 422


def test_register_duplicate_email_returns_400(client, db_session):
    existing = make_user(db_session)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": existing.email.upper(), "password": PASSWORD, "name": "Dup"},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "BAD_REQUEST"


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/v1/auth/register", json={"email": unique_email(), "password": "short", "name": "X"}
    )

    assert response.status_code == 422


# --- login ------------------------------------------------------------------
def test_login_returns_bearer_token_with_role(client, db_session):
    user = make_user(db_session, role="MAINTENANCE_MANAGER")
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": PASSWORD})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    me = client.get("/api/v1/users", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 403  # valid token, but not ADMIN


def test_login_wrong_password_returns_401(client, db_session):
    user = make_user(db_session)
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": unique_email(), "password": PASSWORD}
    )

    assert response.status_code == 401


def test_login_inactive_user_returns_401(client, db_session):
    user = make_user(db_session, is_active=False)
    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": PASSWORD})

    assert response.status_code == 401


def test_register_then_login_flow(client):
    email = unique_email()
    client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD, "name": "N"})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["access_token"]


# --- token validation / logout -----------------------------------------------
def test_logout_requires_token(client):
    assert client.post("/api/v1/auth/logout").status_code == 401


def test_logout_with_valid_token(client, db_session):
    user = make_user(db_session)
    response = client.post("/api/v1/auth/logout", headers=auth_header(user))

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}


def test_expired_token_is_rejected(client, db_session):
    user = make_user(db_session, role="ADMIN")
    token = create_access_token({"sub": str(user.id), "role": "ADMIN"}, timedelta(seconds=-5))
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_garbage_token_is_rejected(client):
    response = client.get("/api/v1/users", headers={"Authorization": "Bearer not.a.jwt"})

    assert response.status_code == 401


def test_token_for_deleted_user_is_rejected(client):
    token = create_access_token({"sub": str(uuid.uuid4()), "role": "ADMIN"})
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_token_for_deactivated_user_is_rejected(client, db_session):
    user = make_user(db_session, role="ADMIN", is_active=False)

    assert client.get("/api/v1/users", headers=auth_header(user)).status_code == 401


def test_role_claim_in_token_is_not_trusted(client, db_session):
    engineer = make_user(db_session)
    token = create_access_token({"sub": str(engineer.id), "role": "ADMIN"})
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403


# --- RBAC: users --------------------------------------------------------------
def test_list_users_requires_authentication(client):
    assert client.get("/api/v1/users").status_code == 401


@pytest.mark.parametrize("role", ["MAINTENANCE_MANAGER", "MAINTENANCE_ENGINEER"])
def test_list_users_forbidden_for_non_admin(client, db_session, role):
    user = make_user(db_session, role=role)
    response = client.get("/api/v1/users", headers=auth_header(user))

    assert response.status_code == 403
    assert response.json()["error"] == "FORBIDDEN"


def test_admin_can_list_users(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    engineer = make_user(db_session)
    response = client.get("/api/v1/users?limit=100", headers=auth_header(admin))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    emails = {item["email"] for item in body["items"]}
    assert {admin.email, engineer.email} <= emails
    assert all("password_hash" not in item for item in body["items"])


def test_admin_can_filter_users_by_role(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    make_user(db_session, role="MAINTENANCE_MANAGER")
    response = client.get(
        "/api/v1/users?role=MAINTENANCE_MANAGER&limit=100", headers=auth_header(admin)
    )

    assert response.status_code == 200
    assert {item["role"] for item in response.json()["items"]} == {"MAINTENANCE_MANAGER"}


def test_admin_can_update_role(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role",
        json={"role": "MAINTENANCE_MANAGER"},
        headers=auth_header(admin),
    )

    assert response.status_code == 200
    assert response.json()["role"] == "MAINTENANCE_MANAGER"
    db_session.refresh(engineer)
    assert engineer.role == "MAINTENANCE_MANAGER"


def test_non_admin_cannot_update_role(client, db_session):
    manager = make_user(db_session, role="MAINTENANCE_MANAGER")
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role", json={"role": "ADMIN"}, headers=auth_header(manager)
    )

    assert response.status_code == 403


def test_engineer_cannot_promote_self(client, db_session):
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role", json={"role": "ADMIN"}, headers=auth_header(engineer)
    )

    assert response.status_code == 403


def test_update_role_unknown_user_returns_404(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    response = client.patch(
        f"/api/v1/users/{uuid.uuid4()}/role", json={"role": "ADMIN"}, headers=auth_header(admin)
    )

    assert response.status_code == 404


def test_update_role_rejects_invalid_role(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    engineer = make_user(db_session)
    response = client.patch(
        f"/api/v1/users/{engineer.id}/role", json={"role": "PILOT"}, headers=auth_header(admin)
    )

    assert response.status_code == 422


def test_admin_cannot_demote_self(client, db_session):
    admin = make_user(db_session, role="ADMIN")
    response = client.patch(
        f"/api/v1/users/{admin.id}/role",
        json={"role": "MAINTENANCE_ENGINEER"},
        headers=auth_header(admin),
    )

    assert response.status_code == 400
