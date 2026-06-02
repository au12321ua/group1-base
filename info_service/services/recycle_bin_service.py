"""RecycleBinService — soft-deleted user listing, restore, and physical deletion."""

import logging

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.core.config import get_info_settings
from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.services.auth_client import batch_fetch_role_names
from shared.exceptions import BusinessRuleError, ResourceNotFoundError

logger = logging.getLogger("recycle_bin_service")


class RecycleBinService:
    """Manages the soft-deleted user recycle bin."""

    def __init__(self) -> None:
        self._settings = get_info_settings()

    @staticmethod
    def _get_client():
        from info_service.services.auth_http_client import get_auth_service_client
        return get_auth_service_client()

    async def _call_auth_enable(self, user_id: int) -> None:
        """POST /internal/users/{id}/enable. Raises on failure."""
        try:
            resp = await self._get_client().post_internal(
                f"/users/{user_id}/enable"
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Auth enable returned {resp.status_code}")
        except Exception:
            logger.exception("Failed to enable user %s in Auth", user_id)
            raise

    async def _call_auth_delete(self, user_id: int) -> None:
        """DELETE /internal/users/{id}. Raises on failure."""
        try:
            resp = await self._get_client().delete_internal(
                f"/users/{user_id}"
            )
            if resp.status_code != 204:
                raise RuntimeError(f"Auth delete returned {resp.status_code}")
        except Exception:
            logger.exception("Failed to delete user %s in Auth", user_id)
            raise

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
            only_deleted=True,
        )

        # Batch-fetch profiles (fix N+1)
        user_info_ids = [u.id for u in items]
        profile_map = await user_profile_crud.get_by_user_ids(db, user_info_ids)

        # Batch-fetch roles from Auth
        role_map = await batch_fetch_role_names(self._settings, user_info_ids)

        result = []
        for u in items:
            profile = profile_map.get(u.id)
            full_name = profile.full_name if profile else ""
            result.append({
                "id": u.id,
                "user_no": u.user_no,
                "username": u.username,
                "full_name": full_name,
                "role_ids": "",
                "role_names": role_map.get(u.id, []),
                "is_deleted": u.is_deleted,
                "deleted_at": u.deleted_at,
            })

        return result, total

    async def restore_user(self, db: AsyncSession, user_id: int) -> None:
        """Restore a soft-deleted user: clear isDeleted → HTTP enable Auth account."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        if not user.is_deleted:
            raise BusinessRuleError("User is not deleted, cannot restore")

        await user_crud.restore(db, user_id)

        # Sync to Auth — with compensation
        try:
            await self._call_auth_enable(user_id)
        except Exception:
            # Compensate: re-mark as deleted
            await user_crud.logical_delete(db, user_id)
            await db.flush()
            raise BusinessRuleError(
                "Failed to enable user in Auth Service; Info DB rolled back"
            )

    async def physical_delete_user(self, db: AsyncSession, user_id: int) -> None:
        """Permanently delete user from Info DB + call Auth cleanup."""
        user = await user_crud.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        if not user.is_deleted:
            raise BusinessRuleError("User must be soft-deleted before physical deletion")

        # Delete profile first (FK constraint)
        await user_profile_crud.delete(db, user_id)
        # Delete user record
        await user_crud.physical_delete(db, user_id)

        # Try Auth cleanup — best effort for physical delete
        try:
            await self._call_auth_delete(user_id)
        except Exception:
            logger.warning("Auth cleanup failed for user %s during physical delete", user_id)

    async def batch_physical_delete(self, db: AsyncSession, user_ids: list[int]) -> None:
        """Permanently delete multiple users with independent error handling."""
        for user_id in user_ids:
            try:
                async with db.begin_nested():
                    await self.physical_delete_user(db, user_id)
            except Exception as e:
                logger.warning("Failed to physical delete user %s: %s", user_id, e)


recycle_bin_service = RecycleBinService()
