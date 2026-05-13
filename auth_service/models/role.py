"""Role and UserRole models for RBAC."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Role(SQLModel, table=True):
    """Role definition."""

    __tablename__ = "roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=64, unique=True, index=True)
    name: str = Field(max_length=128)
    description: str = Field(default="", max_length=512)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRole(SQLModel, table=True):
    """Many-to-many association between users and roles."""

    __tablename__ = "user_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    role_id: int = Field(foreign_key="roles.id")
