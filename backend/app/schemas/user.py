import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MAINTENANCE_MANAGER = "MAINTENANCE_MANAGER"
    MAINTENANCE_ENGINEER = "MAINTENANCE_ENGINEER"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    role: UserRole
    is_active: bool


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class UserRoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: UserRole
