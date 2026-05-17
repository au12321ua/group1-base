"""Role CRUD — role management and user-role assignments."""

import warnings

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.role import Role


class RoleCRUD:
    """Data access for Role and UserRole models."""

    def __init__(self) -> None:
        warnings.warn("TODO: RoleCRUD — implement all methods")

    async def get_by_code(self, db: AsyncSession, code: str) -> Role | None:
        """Get role by its code."""
        warnings.warn("TODO: implement get_by_code")
        result = await db.exec(select(Role).where(Role.code == code))
        return result.first()

    async def get_user_roles(self, db: AsyncSession, user_id: str) -> list[Role]:
        """Get all roles assigned to a user."""
        warnings.warn("TODO: implement get_user_roles — join query")
        raise NotImplementedError("get_user_roles not implemented")

    async def assign_roles(self, db: AsyncSession, user_id: str, role_ids: list[int]) -> None:
        """Replace all role assignments for a user (delete old, insert new)."""
        warnings.warn("TODO: implement assign_roles — transactional replace")
        raise NotImplementedError("assign_roles not implemented")

    async def remove_all_roles(self, db: AsyncSession, user_id: str) -> None:
        """Remove all role assignments for a user."""
        warnings.warn("TODO: implement remove_all_roles")
        raise NotImplementedError("remove_all_roles not implemented")

    async def list_all(self, db: AsyncSession) -> list[Role]:
        """List all active roles."""
        warnings.warn("TODO: implement list_all")
        result = await db.exec(select(Role).where(Role.is_active))
        # result.all() returns a Sequence[Role]; convert to list for the declared return type
        return list(result.all())


role_crud = RoleCRUD()
