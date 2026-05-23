"""Permission and RolePermission models for RBAC."""

from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Permission(SQLModel, table=True):
    """Permission point definition using resource:action format."""

    __tablename__: str = "permissions"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=128, unique=True, index=True)
    name: str = Field(max_length=256)
    resource: str = Field(max_length=64)
    action: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RolePermission(SQLModel, table=True):
    """Many-to-many association between roles and permissions."""

    __tablename__: str = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "role_id", "permission_id", name="uq_role_permissions_role_id_permission_id"
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id")
    permission_id: int = Field(foreign_key="permissions.id")
