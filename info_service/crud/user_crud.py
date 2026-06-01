"""UserInfo CRUD — main user table operations."""

from datetime import UTC, datetime

from sqlalchemy import or_
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile


class UserCRUD:
    """Data access for UserInfo model."""

    async def get_by_id(self, db: AsyncSession, user_id: int) -> UserInfo | None:
        """Get user by primary key."""
        result = await db.exec(select(UserInfo).where(UserInfo.id == user_id))
        return result.first()

    async def get_by_user_no(self, db: AsyncSession, user_no: str) -> UserInfo | None:
        """Get user by user_no (unique)."""
        result = await db.exec(select(UserInfo).where(UserInfo.user_no == user_no))
        return result.first()

    async def get_by_username(self, db: AsyncSession, username: str) -> UserInfo | None:
        """Get user by username (unique)."""
        result = await db.exec(select(UserInfo).where(UserInfo.username == username))
        return result.first()

    # Whitelist of allowed sort columns
    _SORT_FIELDS: dict[str, str] = {
        "id": "id",
        "user_no": "user_no",
        "username": "username",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        keyword: str | None = None,
        status: str | None = None,
        include_deleted: bool = False,
        only_deleted: bool = False,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> tuple[list[UserInfo], int]:
        """Get paginated user list with optional filters. Returns (items, total).

        Role-based filtering is not supported here — roles are managed
        by Auth Service, not stored in Info Service.
        """
        conditions = []
        if only_deleted:
            conditions.append(UserInfo.is_deleted == True)  # noqa: E712
        elif not include_deleted:
            conditions.append(UserInfo.is_deleted == False)  # noqa: E712

        if keyword:
            # Search in user_no, username, and via profile full_name
            profile_match = (
                select(UserProfile.user_id)
                .where(UserProfile.full_name.contains(keyword))
            )
            conditions.append(
                or_(
                    UserInfo.user_no.contains(keyword),
                    UserInfo.username.contains(keyword),
                    UserInfo.id.in_(profile_match),
                )
            )

        if status:
            # status is stored in UserProfile
            profile_status_match = (
                select(UserProfile.user_id)
                .where(UserProfile.status == status)
            )
            conditions.append(UserInfo.id.in_(profile_status_match))

        base_query = select(UserInfo).where(*conditions)
        count_query = select(func.count()).select_from(UserInfo).where(*conditions)

        total_result = await db.exec(count_query)
        total = total_result.one()

        # Dynamic sorting with whitelist validation
        col_name = self._SORT_FIELDS.get(sort_by, "id")
        sort_col = getattr(UserInfo, col_name)
        if sort_order == "desc":
            base_query = base_query.order_by(sort_col.desc())
        else:
            base_query = base_query.order_by(sort_col.asc())

        items_result = await db.exec(base_query.offset(skip).limit(limit))
        return list(items_result.all()), total

    async def create(self, db: AsyncSession, user: UserInfo) -> UserInfo:
        """Create a new user record."""
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, user: UserInfo, **kwargs) -> UserInfo:
        """Update user fields."""
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(user)
        return user

    async def logical_delete(self, db: AsyncSession, user_id: int) -> None:
        """Mark user as deleted (is_deleted=True, set deleted_at)."""
        user = await self.get_by_id(db, user_id)
        if user:
            user.is_deleted = True
            user.deleted_at = datetime.now(UTC)
            await db.flush()

    async def restore(self, db: AsyncSession, user_id: int) -> None:
        """Clear isDeleted flag and deleted_at."""
        user = await self.get_by_id(db, user_id)
        if user:
            user.is_deleted = False
            user.deleted_at = None
            await db.flush()

    async def physical_delete(self, db: AsyncSession, user_id: int) -> None:
        """Permanently delete user record."""
        user = await self.get_by_id(db, user_id)
        if user:
            await db.delete(user)
            await db.flush()


user_crud = UserCRUD()
