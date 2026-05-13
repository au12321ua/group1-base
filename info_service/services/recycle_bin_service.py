"""RecycleBinService — soft-deleted user listing, restore, and physical deletion."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession


class RecycleBinService:
    """Manages the soft-deleted user recycle bin."""

    def __init__(self) -> None:
        warnings.warn("TODO: RecycleBinService — implement all methods")

    async def list_deleted_users(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20, keyword: str | None = None
    ) -> tuple[list, int]:
        """List users with is_deleted=True. Returns (items, total)."""
        warnings.warn("TODO: implement list_deleted_users")
        raise NotImplementedError("list_deleted_users not implemented")

    async def restore_user(self, db: AsyncSession, user_id: int) -> None:
        """Restore a soft-deleted user: clear isDeleted → HTTP enable Auth account."""
        warnings.warn("TODO: implement restore_user — cross-service enable call")
        raise NotImplementedError("restore_user not implemented")

    async def physical_delete_user(self, db: AsyncSession, user_id: int) -> None:
        """Permanently delete user from Info DB + call Auth cleanup. Write audit log."""
        warnings.warn("TODO: implement physical_delete_user — cascade delete + audit")
        raise NotImplementedError("physical_delete_user not implemented")

    async def batch_physical_delete(self, db: AsyncSession, user_ids: list[int]) -> None:
        """Permanently delete multiple users."""
        warnings.warn("TODO: implement batch_physical_delete")
        raise NotImplementedError("batch_physical_delete not implemented")


recycle_bin_service = RecycleBinService()
