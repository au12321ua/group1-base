"""CourseSchedule CRUD — scheduling operations."""

import warnings

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.course_schedule import CourseSchedule


class ScheduleCRUD(BaseCRUD[CourseSchedule]):
    """Data access for CourseSchedule model."""

    def __init__(self) -> None:
        super().__init__(CourseSchedule)
        warnings.warn("TODO: ScheduleCRUD — implement custom query methods")

    async def get_by_offering(
        self, db: AsyncSession, offering_id: int
    ) -> list[CourseSchedule]:
        """Get all schedules for an offering."""
        warnings.warn("TODO: implement get_by_offering")
        raise NotImplementedError("get_by_offering not implemented")

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
        warnings.warn("TODO: implement check_conflict")
        raise NotImplementedError("check_conflict not implemented")


schedule_crud = ScheduleCRUD()
