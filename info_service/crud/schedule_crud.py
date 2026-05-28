"""CourseSchedule CRUD — scheduling operations."""

from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.course_schedule import CourseSchedule


class ScheduleCRUD(BaseCRUD[CourseSchedule]):
    """Data access for CourseSchedule model."""

    def __init__(self) -> None:
        super().__init__(CourseSchedule)

    async def get_by_offering(
        self, db: AsyncSession, offering_id: int
    ) -> list[CourseSchedule]:
        """Get all schedules for an offering."""
        stmt = (
            select(CourseSchedule)
            .where(CourseSchedule.offering_id == offering_id)
            .order_by(
                CourseSchedule.day_of_week,
                CourseSchedule.start_period,
                CourseSchedule.id,
            )
        )
        result = await db.exec(stmt)
        return list(result.all())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        offering_id: int | None = None,
        classroom_id: int | None = None,
        day_of_week: int | None = None,
    ) -> tuple[list[CourseSchedule], int]:
        """Get paginated schedules with basic filters."""
        conditions = []
        if offering_id is not None:
            conditions.append(CourseSchedule.offering_id == offering_id)
        if classroom_id is not None:
            conditions.append(CourseSchedule.classroom_id == classroom_id)
        if day_of_week is not None:
            conditions.append(CourseSchedule.day_of_week == day_of_week)

        stmt = (
            select(CourseSchedule)
            .where(*conditions)
            .order_by(
                CourseSchedule.day_of_week,
                CourseSchedule.start_period,
                CourseSchedule.id,
            )
            .offset(skip)
            .limit(limit)
        )
        count_stmt = select(func.count(CourseSchedule.id)).where(*conditions)

        items = list((await db.exec(stmt)).all())
        total = (await db.exec(count_stmt)).one()
        return items, total

    async def check_conflict(
        self,
        db: AsyncSession,
        classroom_id: int,
        day_of_week: int,
        start_period: int,
        end_period: int,
        exclude_id: int | None = None,
    ) -> bool:
        """Check for time/room conflicts. Returns True if conflict exists."""
        conditions = [
            CourseSchedule.classroom_id == classroom_id,
            CourseSchedule.day_of_week == day_of_week,
            and_(
                CourseSchedule.start_period <= end_period,
                CourseSchedule.end_period >= start_period,
            ),
        ]
        if exclude_id is not None:
            conditions.append(CourseSchedule.id != exclude_id)

        stmt = select(CourseSchedule.id).where(*conditions).limit(1)
        return (await db.exec(stmt)).first() is not None


schedule_crud = ScheduleCRUD()
