"""Role and UserRole models for RBAC."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Role(SQLModel, table=True):
    """Role definition."""

    __tablename__: str = "roles"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=64, unique=True, index=True)
    name: str = Field(max_length=128)
    description: str = Field(default="", max_length=512)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))


class UserRole(SQLModel, table=True):
    """Many-to-many association between users and roles."""

    __tablename__: str = "user_roles"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    role_id: int = Field(foreign_key="roles.id")
