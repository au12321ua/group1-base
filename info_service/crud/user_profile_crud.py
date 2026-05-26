"""UserProfile CRUD — profile table operations."""

from datetime import UTC, datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.models.user_profile import UserProfile


class UserProfileCRUD:
    """Data access for UserProfile model."""

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> UserProfile | None:
        """Get profile by user_id."""
        result = await db.exec(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.first()

    async def create(self, db: AsyncSession, profile: UserProfile) -> UserProfile:
        """Create a new user profile."""
        db.add(profile)
        await db.flush()
        await db.refresh(profile)
        return profile

    async def update(
        self, db: AsyncSession, profile: UserProfile, **kwargs
    ) -> UserProfile:
        """Update profile fields."""
        for field, value in kwargs.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        profile.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(profile)
        return profile

    async def delete(self, db: AsyncSession, user_id: int) -> None:
        """Delete profile by user_id."""
        profile = await self.get_by_user_id(db, user_id)
        if profile:
            await db.delete(profile)
            await db.flush()


user_profile_crud = UserProfileCRUD()
