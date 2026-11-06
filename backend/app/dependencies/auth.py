import uuid
from collections.abc import Callable, Iterable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

# auto_error=False so a missing header yields 401 (not FastAPI's default 403).
bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(message: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(str(payload["sub"]))
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token has expired")
    except (jwt.PyJWTError, ValueError, KeyError):
        raise _unauthorized()

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise _unauthorized()

    return user


def require_role(allowed_roles: Iterable[str]) -> Callable[..., User]:
    """Dependency factory: allow only users whose role is in allowed_roles.

    The role is read from the database user, not the token, so role changes
    take effect immediately.
    """
    allowed = frozenset(str(getattr(role, "value", role)) for role in allowed_roles)

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
