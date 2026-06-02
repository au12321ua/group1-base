"""UserProfile CRUD — profile table operations."""

from datetime import UTC, datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile


class UserProfileCRUD:
    """Data access for UserProfile model."""

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> UserProfile | None:
        """Get profile by user_id."""
        result = await db.exec(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.first()

    async def get_by_user_ids(
        self, db: AsyncSession, user_ids: list[int]
    ) -> dict[int, UserProfile]:
        """Batch get profiles by user_ids, returning {user_id: UserProfile} map."""
        if not user_ids:
            return {}
        result = await db.exec(
            select(UserProfile).where(UserProfile.user_id.in_(user_ids))
        )
        return {p.user_id: p for p in result.all()}

    async def batch_get_display_names(
        self, db: AsyncSession, user_nos: set[str],
        *, fallback_to_username: bool = True,
    ) -> dict[str, str]:
        """Batch-fetch display names by user_no strings using a single JOIN.

        Returns {user_no: full_name} map. When *fallback_to_username* is True
        and no UserProfile row exists, falls back to UserInfo.username.
        """
        if not user_nos:
            return {}
        stmt = (
            select(UserInfo.user_no, UserProfile.full_name, UserInfo.username)
            .outerjoin(UserProfile, UserInfo.id == UserProfile.user_id)
            .where(UserInfo.user_no.in_(user_nos))
        )
        result = await db.exec(stmt)
        name_map: dict[str, str] = {}
        for user_no, full_name, username in result.all():
            if full_name:
                name_map[user_no] = full_name
            elif fallback_to_username:
                name_map[user_no] = username or ""
            else:
                name_map[user_no] = ""
        return name_map

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
