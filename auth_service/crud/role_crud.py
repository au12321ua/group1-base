"""Role CRUD — role management and user-role assignments."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.role import Role, UserRole


class RoleCRUD:
    """Data access for Role and UserRole models."""

    async def get_by_id(self, db: AsyncSession, role_id: int) -> Role | None:
        """Get role by primary key."""
        result = await db.exec(select(Role).where(Role.id == role_id))
        return result.first()

    async def get_by_code(self, db: AsyncSession, code: str) -> Role | None:
        """Get role by its code."""
        result = await db.exec(select(Role).where(Role.code == code))
        return result.first()

    async def get_user_roles(self, db: AsyncSession, user_id: str) -> list[Role]:
        """Get all roles assigned to a user."""
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await db.exec(stmt)
        return list(result.all())

    async def assign_roles(self, db: AsyncSession, user_id: str, role_ids: list[int]) -> None:
        """Replace all role assignments for a user (delete old, insert new)."""
        existing = await db.exec(select(UserRole).where(UserRole.user_id == user_id))
        for user_role in existing.all():
            await db.delete(user_role)
        for role_id in role_ids:
            db.add(UserRole(user_id=user_id, role_id=role_id))
        await db.flush()

    async def remove_all_roles(self, db: AsyncSession, user_id: str) -> None:
        """Remove all role assignments for a user."""
        result = await db.exec(select(UserRole).where(UserRole.user_id == user_id))
        for user_role in result.all():
            await db.delete(user_role)
        await db.flush()

    async def list_all(self, db: AsyncSession) -> list[Role]:
        """List all active roles."""
        result = await db.exec(select(Role).where(Role.is_active.is_(True)))
        return list(result.all())


role_crud = RoleCRUD()
