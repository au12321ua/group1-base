"""CourseOffering CRUD — offering instance operations."""

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.course_offering import CourseOffering


class OfferingCRUD(BaseCRUD[CourseOffering]):
    """Data access for CourseOffering model."""

    def __init__(self) -> None:
        super().__init__(CourseOffering)

    async def batch_get_by_ids(
        self, db: AsyncSession, ids: set[int]
    ) -> dict[int, CourseOffering]:
        """Batch-fetch offerings by IDs in a single query, returning {id: CourseOffering} map."""
        if not ids:
            return {}
        stmt = select(CourseOffering).where(CourseOffering.id.in_(ids))
        result = await db.exec(stmt)
        return {o.id: o for o in result.all()}

    async def get_by_course_and_term(
        self, db: AsyncSession, course_id: int, term_code: str
    ) -> list[CourseOffering]:
        """Get all offerings for a course in a term."""
        stmt = (
            select(CourseOffering)
            .where(
                CourseOffering.course_id == course_id,
                CourseOffering.term_code == term_code,
            )
            .order_by(CourseOffering.id)
        )
        result = await db.exec(stmt)
        return list(result.all())

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
        conditions = []
        if course_id is not None:
            conditions.append(CourseOffering.course_id == course_id)
        if term_code:
            conditions.append(CourseOffering.term_code == term_code)
        if status:
            conditions.append(CourseOffering.status == status)

        stmt = (
            select(CourseOffering)
            .where(*conditions)
            .offset(skip)
            .limit(limit)
            .order_by(CourseOffering.id)
        )
        count_stmt = select(func.count(CourseOffering.id)).where(*conditions)

        items = list((await db.exec(stmt)).all())
        total = (await db.exec(count_stmt)).one()
        return items, total


offering_crud = OfferingCRUD()
