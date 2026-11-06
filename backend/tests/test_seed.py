import pytest
from app.core.security import verify_password
from app.db.seed import DEMO_ACCOUNTS, SeedError, resolve_passwords, seed_demo_users
from app.models.user import User
from sqlalchemy import select

ENV = {account.env_var: f"{account.key.lower()}-demo-pass-123" for account in DEMO_ACCOUNTS}


def demo_users(db_session):
    emails = [account.email for account in DEMO_ACCOUNTS]
    return db_session.execute(select(User).where(User.email.in_(emails))).scalars().all()


@pytest.fixture
def clean_demo_users(db_session):
    # Rolled back by the db_session fixture after the test.
    for user in demo_users(db_session):
        db_session.delete(user)
    db_session.flush()


def test_resolve_passwords_from_env():
    passwords = resolve_passwords(ENV)

    assert set(passwords) == {"admin@prognex.com", "manager@prognex.com", "engineer@prognex.com"}


def test_resolve_passwords_fails_without_env_or_prompt():
    with pytest.raises(SeedError):
        resolve_passwords({})


def test_resolve_passwords_uses_prompt_for_missing_values():
    passwords = resolve_passwords({}, prompt=lambda _: "prompted-pass-123")

    assert set(passwords.values()) == {"prompted-pass-123"}


def test_resolve_passwords_rejects_short_password():
    with pytest.raises(SeedError):
        resolve_passwords({**ENV, "PROGNEX_SEED_ADMIN_PASSWORD": "short"})


def test_seed_creates_three_roles_with_hashed_passwords(db_session, clean_demo_users):
    passwords = resolve_passwords(ENV)
    result = seed_demo_users(db_session, passwords)

    assert len(result["created"]) == 3
    users = {user.email: user for user in demo_users(db_session)}
    assert users["admin@prognex.com"].role == "ADMIN"
    assert users["manager@prognex.com"].role == "MAINTENANCE_MANAGER"
    assert users["engineer@prognex.com"].role == "MAINTENANCE_ENGINEER"
    for email, user in users.items():
        assert user.password_hash.startswith("$argon2id$")
        assert verify_password(passwords[email], user.password_hash)


def test_seed_is_idempotent(db_session, clean_demo_users):
    passwords = resolve_passwords(ENV)
    seed_demo_users(db_session, passwords)
    original_hash = next(u for u in demo_users(db_session) if u.role == "ADMIN").password_hash

    second = seed_demo_users(db_session, {})

    assert second["created"] == []
    assert len(second["skipped"]) == 3
    assert len(demo_users(db_session)) == 3
    admin = next(u for u in demo_users(db_session) if u.role == "ADMIN")
    assert admin.password_hash == original_hash
