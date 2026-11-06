from datetime import timedelta

import jwt
import pytest
from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_uses_argon2id_and_salts():
    first = hash_password("correct horse battery")
    second = hash_password("correct horse battery")

    assert first.startswith("$argon2id$")
    assert first != second
    assert "correct horse battery" not in first


def test_verify_password_accepts_correct_and_rejects_wrong():
    hashed = hash_password("correct horse battery")

    assert verify_password("correct horse battery", hashed) is True
    assert verify_password("wrong password!!", hashed) is False


def test_verify_password_rejects_malformed_hash():
    assert verify_password("anything", "not-a-hash") is False


def test_access_token_contains_sub_role_and_expiry():
    token = create_access_token({"sub": "user-123", "role": "ADMIN"})
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    assert payload["sub"] == "user-123"
    assert payload["role"] == "ADMIN"
    assert payload["exp"] - payload["iat"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_default_expiry_is_twelve_hours():
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 720
    assert settings.JWT_ALGORITHM == "HS256"


def test_custom_expires_delta():
    token = create_access_token({"sub": "u", "role": "ADMIN"}, timedelta(minutes=5))
    payload = decode_access_token(token)

    assert payload["exp"] - payload["iat"] == 300


def test_expired_token_is_rejected():
    token = create_access_token({"sub": "u", "role": "ADMIN"}, timedelta(seconds=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_token_signed_with_other_key_is_rejected():
    forged = jwt.encode({"sub": "u", "role": "ADMIN", "exp": 9999999999}, "other-key", "HS256")

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(forged)


def test_create_access_token_requires_sub_and_role():
    with pytest.raises(ValueError):
        create_access_token({"sub": "u"})
