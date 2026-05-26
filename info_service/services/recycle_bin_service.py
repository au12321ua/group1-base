"""RecycleBinService — soft-deleted user listing, restore, and physical deletion."""

import logging

import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.core.config import get_info_settings
from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from shared.exceptions import BusinessRuleError, ResourceNotFoundError

logger = logging.getLogger("recycle_bin_service")


class RecycleBinService:
    """Manages the soft-deleted user recycle bin."""

    def __init__(self) -> None:
        self._settings = get_info_settings()

    def _auth_url(self, path: str) -> str:
        return f"{self._settings.auth_service_url}/api/v1/internal{path}"

    async def _call_auth_enable(self, user_id: int) -> bool:
        """POST /internal/users/{id}/enable."""
        try:
            async with httpx.AsyncClient(
                timeout=self._settings.auth_service_timeout
            ) as client:
                resp = await client.post(
                    self._auth_url(f"/users/{user_id}/enable")
                )
                return resp.status_code == 200
        except Exception:
            logger.exception("Failed to enable user %s in Auth", user_id)
            return False

    async def _call_auth_delete(self, user_id: int) -> bool:
        """DELETE /internal/users/{id}."""
        try:
            async with httpx.AsyncClient(
                timeout=self._settings.auth_service_timeout
            ) as client:
                resp = await client.delete(
                    self._auth_url(f"/users/{user_id}")
                )
                return resp.status_code == 204
        except Exception:
            logger.exception("Failed to delete user %s in Auth", user_id)
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def list_deleted_users(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
    ) -> tuple[list, int]:
        """List users with is_deleted=True. Returns (items, total)."""
        skip = (page - 1) * page_size
        items, total = await user_crud.get_multi(
            db,
            skip=skip,
            limit=page_size,
            keyword=keyword,
            include_deleted=True,
        )
        # Only return deleted users
        deleted = [u for u in items if u.is_deleted]
        return deleted, len(deleted)

    async def restore_user(self, db: AsyncSession, user_id: int) -> None:
        """Restore a soft-deleted user: clear isDeleted → HTTP enable Auth account."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        if not user.is_deleted:
            raise BusinessRuleError("User is not deleted, cannot restore")

        await user_crud.restore(db, user_id)

        # Best-effort enable in Auth
        await self._call_auth_enable(user_id)

    async def physical_delete_user(self, db: AsyncSession, user_id: int) -> None:
        """Permanently delete user from Info DB + call Auth cleanup."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))

        # Delete profile first (FK constraint)
        await user_profile_crud.delete(db, user_id)
        # Delete user record
        await user_crud.physical_delete(db, user_id)

        # Best-effort delete in Auth
        await self._call_auth_delete(user_id)

    async def batch_physical_delete(self, db: AsyncSession, user_ids: list[int]) -> None:
        """Permanently delete multiple users."""
        for user_id in user_ids:
            try:
                await self.physical_delete_user(db, user_id)
            except Exception as e:
                logger.warning("Failed to physical delete user %s: %s", user_id, e)


recycle_bin_service = RecycleBinService()
