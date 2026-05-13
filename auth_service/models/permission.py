"""Permission and RolePermission models for RBAC."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Permission(SQLModel, table=True):
    """Permission point definition using resource:action format."""

    __tablename__ = "permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=128, unique=True, index=True)
    name: str = Field(max_length=256)
    resource: str = Field(max_length=64)
    action: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RolePermission(SQLModel, table=True):
    """Many-to-many association between roles and permissions."""

    __tablename__ = "role_permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id")
    permission_id: int = Field(foreign_key="permissions.id")
