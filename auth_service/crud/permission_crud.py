"""Permission CRUD — permission definitions and role-permission mapping."""

import warnings

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.permission import Permission


class PermissionCRUD:
    """Data access for Permission and RolePermission models."""

    def __init__(self) -> None:
        warnings.warn("TODO: PermissionCRUD — implement all methods")

    async def get_by_code(self, db: AsyncSession, code: str) -> Permission | None:
        """Get permission by its code."""
        warnings.warn("TODO: implement get_by_code")
        result = await db.exec(select(Permission).where(Permission.code == code))
        return result.first()

    async def get_role_permissions(self, db: AsyncSession, role_id: int) -> list[Permission]:
        """Get all permissions for a role."""
        warnings.warn("TODO: implement get_role_permissions — join query")
        raise NotImplementedError("get_role_permissions not implemented")

    async def get_user_permissions(self, db: AsyncSession, user_id: str) -> list[str]:
        """Get all permission codes for a user (via user_roles → role_permissions)."""
        warnings.warn("TODO: implement get_user_permissions — triple join query")
        raise NotImplementedError("get_user_permissions not implemented")


permission_crud = PermissionCRUD()
