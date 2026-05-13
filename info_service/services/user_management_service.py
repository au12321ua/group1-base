"""UserManagementService — user lifecycle, cross-service sync, batch import."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.schemas.user_schema import (
    UserCreateRequest,
    UserImportResult,
    UserPatchRequest,
    UserResponse,
    UserUpdateRequest,
)


class UserManagementService:
    """Full user lifecycle management with cross-service coordination."""

    def __init__(self) -> None:
        warnings.warn("TODO: UserManagementService — implement all methods")

    async def create_user(self, db: AsyncSession, request: UserCreateRequest) -> UserResponse:
        """Create a user: write Info DB → HTTP call Auth Service /internal/users → compensate on failure."""
        warnings.warn("TODO: implement create_user — cross-service sync with compensation")
        raise NotImplementedError("create_user not implemented")

    async def update_user(self, db: AsyncSession, user_id: int, request: UserUpdateRequest) -> UserResponse:
        """Full update user info."""
        warnings.warn("TODO: implement update_user")
        raise NotImplementedError("update_user not implemented")

    async def patch_user(self, db: AsyncSession, user_id: int, request: UserPatchRequest) -> UserResponse:
        """Partial update user info. If role_ids changed, sync to Auth Service."""
        warnings.warn("TODO: implement patch_user — role sync on role_ids change")
        raise NotImplementedError("patch_user not implemented")

    async def get_user(self, db: AsyncSession, user_id: int) -> UserResponse:
        """Get user detail with profile."""
        warnings.warn("TODO: implement get_user")
        raise NotImplementedError("get_user not implemented")

    async def list_users(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = None,
        role: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[UserResponse], int]:
        """List users with pagination and filters. Returns (items, total)."""
        warnings.warn("TODO: implement list_users")
        raise NotImplementedError("list_users not implemented")

    async def logical_delete_user(self, db: AsyncSession, user_id: int) -> None:
        """Logical delete: mark isDeleted=true → HTTP disable Auth account."""
        warnings.warn("TODO: implement logical_delete_user")
        raise NotImplementedError("logical_delete_user not implemented")

    async def disable_user(self, db: AsyncSession, user_id: int) -> None:
        """Disable a user account."""
        warnings.warn("TODO: implement disable_user")
        raise NotImplementedError("disable_user not implemented")

    async def enable_user(self, db: AsyncSession, user_id: int) -> None:
        """Enable a user account."""
        warnings.warn("TODO: implement enable_user")
        raise NotImplementedError("enable_user not implemented")

    async def batch_import_users(self, db: AsyncSession, csv_content: bytes) -> UserImportResult:
        """Parse CSV → validate each row → create users one-by-one → return summary."""
        warnings.warn("TODO: implement batch_import_users — CSV parsing + batch create")
        raise NotImplementedError("batch_import_users not implemented")


user_management_service = UserManagementService()
