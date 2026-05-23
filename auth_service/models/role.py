"""Role and UserRole models for RBAC."""

from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Role(SQLModel, table=True):
    """Role definition."""

    __tablename__: str = "roles"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=64, unique=True, index=True)
    name: str = Field(max_length=128)
    description: str = Field(default="", max_length=512)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserRole(SQLModel, table=True):
    """Many-to-many association between users and roles."""

    __tablename__: str = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    role_id: int = Field(foreign_key="roles.id")
