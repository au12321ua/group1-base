"""UserInfo CRUD — main user table operations."""

import warnings
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.models.user import UserInfo


class UserCRUD:
    """Data access for UserInfo model."""

    def __init__(self) -> None:
        warnings.warn("TODO: UserCRUD — implement all methods")

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[UserInfo]:
        """Get user by primary key."""
        warnings.warn("TODO: implement get_by_id")
        result = await db.exec(select(UserInfo).where(UserInfo.id == user_id))
        return result.scalars().first()

    async def get_by_user_no(self, db: AsyncSession, user_no: str) -> Optional[UserInfo]:
        """Get user by user_no (unique)."""
        warnings.warn("TODO: implement get_by_user_no")
        result = await db.exec(select(UserInfo).where(UserInfo.user_no == user_no))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[UserInfo]:
        """Get user by username (unique)."""
        warnings.warn("TODO: implement get_by_username")
        result = await db.exec(select(UserInfo).where(UserInfo.username == username))
        return result.scalars().first()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        role: Optional[str] = None,
        include_deleted: bool = False,
    ) -> tuple[list[UserInfo], int]:
        """Get paginated user list with optional filters. Returns (items, total)."""
        warnings.warn("TODO: implement get_multi — build dynamic query")
        raise NotImplementedError("get_multi not implemented")

    async def create(self, db: AsyncSession, user: UserInfo) -> UserInfo:
        """Create a new user record."""
        warnings.warn("TODO: implement create")
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, user: UserInfo, **kwargs) -> UserInfo:
        """Update user fields."""
        warnings.warn("TODO: implement update")
        raise NotImplementedError("update not implemented")

    async def logical_delete(self, db: AsyncSession, user_id: int) -> None:
        """Mark user as deleted (is_deleted=True, set deleted_at)."""
        warnings.warn("TODO: implement logical_delete")
        raise NotImplementedError("logical_delete not implemented")

    async def restore(self, db: AsyncSession, user_id: int) -> None:
        """Clear isDeleted flag and deleted_at."""
        warnings.warn("TODO: implement restore")
        raise NotImplementedError("restore not implemented")

    async def physical_delete(self, db: AsyncSession, user_id: int) -> None:
        """Permanently delete user record."""
        warnings.warn("TODO: implement physical_delete")
        raise NotImplementedError("physical_delete not implemented")


user_crud = UserCRUD()
