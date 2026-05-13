"""CourseOffering CRUD — offering instance operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.course_offering import CourseOffering


class OfferingCRUD(BaseCRUD[CourseOffering]):
    """Data access for CourseOffering model."""

    def __init__(self) -> None:
        super().__init__(CourseOffering)
        warnings.warn("TODO: OfferingCRUD — implement custom query methods")

    async def get_by_course_and_term(
        self, db: AsyncSession, course_id: int, term_code: str
    ) -> list[CourseOffering]:
        """Get all offerings for a course in a term."""
        warnings.warn("TODO: implement get_by_course_and_term")
        raise NotImplementedError("get_by_course_and_term not implemented")

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        course_id: int | None = None,
        term_code: str | None = None,
        status: str | None = None,
    ) -> tuple[list[CourseOffering], int]:
        """Get paginated offering list. Returns (items, total)."""
        warnings.warn("TODO: implement get_multi")
        raise NotImplementedError("get_multi not implemented")


offering_crud = OfferingCRUD()
