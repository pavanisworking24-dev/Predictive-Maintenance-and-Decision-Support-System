import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_role
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse, UserRole, UserRoleUpdate

router = APIRouter(prefix="/users", tags=["Administration"])

admin_only = require_role([UserRole.ADMIN.value])


@router.get("", response_model=UserListResponse)
def list_users(
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(admin_only),
) -> UserListResponse:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role.value)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    users = db.execute(
        query.order_by(User.created_at, User.email).limit(limit).offset(offset)
    ).scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(admin_only),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Prevent an admin from locking themselves (and possibly everyone) out.
    if user.id == current_admin.id and payload.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot remove their own ADMIN role",
        )

    user.role = payload.role.value
    user.updated_at = func.now()
    db.commit()
    db.refresh(user)
    return user
