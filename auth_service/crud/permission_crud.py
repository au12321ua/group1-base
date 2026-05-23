"""Permission CRUD — permission definitions and role-permission mapping."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.permission import Permission, RolePermission
from auth_service.models.role import UserRole


class PermissionCRUD:
    """Data access for Permission and RolePermission models."""

    async def get_by_code(self, db: AsyncSession, code: str) -> Permission | None:
        """Get permission by its code."""
        result = await db.exec(select(Permission).where(Permission.code == code))
        return result.first()

    async def get_role_permissions(self, db: AsyncSession, role_id: int) -> list[Permission]:
        """Get all permissions for a role."""
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        result = await db.exec(stmt)
        return list(result.all())

    async def get_user_permissions(self, db: AsyncSession, user_id: str) -> list[str]:
        """Get all permission codes for a user (via user_roles → role_permissions)."""
        stmt = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id)
            .distinct()
        )
        result = await db.exec(stmt)
        return list(result.all())


permission_crud = PermissionCRUD()
