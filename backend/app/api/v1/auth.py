import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import MessageResponse, Token, UserLogin, UserRegister
from app.schemas.user import UserResponse, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])

DEFAULT_REGISTRATION_ROLE = UserRole.MAINTENANCE_ENGINEER.value

# Hash used when the email is unknown, so login timing does not reveal
# whether an account exists.
_DUMMY_PASSWORD_HASH = hash_password("timing-equaliser-not-a-real-password")


def _find_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(
        select(User).where(func.lower(User.email) == email.lower())
    ).scalar_one_or_none()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> User:
    email = payload.email.lower()

    if _find_user_by_email(db, email) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        role=DEFAULT_REGISTRATION_ROLE,
        is_active=True,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # Concurrent registration with the same email.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = _find_user_by_email(db, payload.email)

    if user is None:
        verify_password(payload.password, _DUMMY_PASSWORD_HASH)
        password_ok = False
    else:
        password_ok = verify_password(payload.password, user.password_hash)

    if not password_ok or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer")


@router.post("/logout", response_model=MessageResponse)
def logout(_: User = Depends(get_current_user)) -> MessageResponse:
    # Tokens are stateless JWTs; the client discards its token.
    return MessageResponse(message="Successfully logged out")
