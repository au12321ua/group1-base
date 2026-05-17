"""UserProfile CRUD — profile table operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.models.user_profile import UserProfile


class UserProfileCRUD:
    """Data access for UserProfile model."""

    def __init__(self) -> None:
        warnings.warn("TODO: UserProfileCRUD — implement all methods")

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> UserProfile | None:
        """Get profile by user_id."""
        warnings.warn("TODO: implement get_by_user_id")
        raise NotImplementedError("get_by_user_id not implemented")

    async def create(self, db: AsyncSession, profile: UserProfile) -> UserProfile:
        """Create a new user profile."""
        warnings.warn("TODO: implement create")
        raise NotImplementedError("create not implemented")

    async def update(self, db: AsyncSession, profile: UserProfile, **kwargs) -> UserProfile:
        """Update profile fields."""
        warnings.warn("TODO: implement update")
        raise NotImplementedError("update not implemented")

    async def delete(self, db: AsyncSession, user_id: int) -> None:
        """Delete profile by user_id."""
        warnings.warn("TODO: implement delete")
        raise NotImplementedError("delete not implemented")


user_profile_crud = UserProfileCRUD()
