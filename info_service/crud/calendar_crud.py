"""AcademicCalendar CRUD — term/semester calendar operations."""

from datetime import date

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.academic_calendar import AcademicCalendar


class CalendarCRUD(BaseCRUD[AcademicCalendar]):
    """Data access for AcademicCalendar model."""

    def __init__(self) -> None:
        super().__init__(AcademicCalendar)

    async def get_by_term_code(self, db: AsyncSession, term_code: str) -> AcademicCalendar | None:
        """Get calendar by term_code."""
        result = await db.exec(
            select(AcademicCalendar).where(AcademicCalendar.term_code == term_code)
        )
        return result.first()

    async def get_by_date(self, db: AsyncSession, d: date) -> AcademicCalendar | None:
        """Get the calendar that covers a specific date."""
        result = await db.exec(
            select(AcademicCalendar).where(
                AcademicCalendar.start_date <= d,
                AcademicCalendar.end_date >= d,
            )
        )
        return result.first()


calendar_crud = CalendarCRUD()
