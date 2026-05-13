"""Course CRUD — course master data operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.course import Course


class CourseCRUD(BaseCRUD[Course]):
    """Data access for Course model."""

    def __init__(self) -> None:
        super().__init__(Course)
        warnings.warn("TODO: CourseCRUD — implement custom query methods")

    async def get_by_course_code(self, db: AsyncSession, code: str) -> Course | None:
        """Get course by course_code (unique)."""
        warnings.warn("TODO: implement get_by_course_code")
        raise NotImplementedError("get_by_course_code not implemented")

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[Course], int]:
        """Get paginated course list. Returns (items, total)."""
        warnings.warn("TODO: implement get_multi")
        raise NotImplementedError("get_multi not implemented")

    async def logical_delete(self, db: AsyncSession, course_id: int) -> None:
        """Soft delete a course."""
        warnings.warn("TODO: implement logical_delete")
        raise NotImplementedError("logical_delete not implemented")


course_crud = CourseCRUD()
