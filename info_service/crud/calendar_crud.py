"""AcademicCalendar CRUD — term/semester calendar operations."""

import warnings
from datetime import date

from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.crud.base import BaseCRUD
from info_service.models.academic_calendar import AcademicCalendar


class CalendarCRUD(BaseCRUD[AcademicCalendar]):
    """Data access for AcademicCalendar model."""

    def __init__(self) -> None:
        super().__init__(AcademicCalendar)
        warnings.warn("TODO: CalendarCRUD — implement custom query methods")

    async def get_by_term_code(self, db: AsyncSession, term_code: str) -> AcademicCalendar | None:
        """Get calendar by term_code."""
        warnings.warn("TODO: implement get_by_term_code")
        raise NotImplementedError("get_by_term_code not implemented")

    async def get_by_date(self, db: AsyncSession, d: date) -> AcademicCalendar | None:
        """Get the calendar that covers a specific date."""
        warnings.warn("TODO: implement get_by_date")
        raise NotImplementedError("get_by_date not implemented")


calendar_crud = CalendarCRUD()
