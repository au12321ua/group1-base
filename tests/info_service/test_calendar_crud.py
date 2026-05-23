"""Unit tests for CalendarCRUD."""

from datetime import date, datetime

import pytest

from info_service.crud.calendar_crud import calendar_crud
from info_service.models.academic_calendar import AcademicCalendar


def _make_calendar(**overrides) -> AcademicCalendar:
    """Create an AcademicCalendar instance with default test values."""
    now = datetime(2025, 9, 1)
    defaults = {
        "term_code": "2025-2026-1",
        "term_name": "2025-2026学年第一学期",
        "start_date": date(2025, 9, 1),
        "end_date": date(2026, 1, 15),
        "version": "1.0",
        "snapshot_time": now,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return AcademicCalendar(**defaults)


@pytest.mark.unit
class TestCalendarCRUD:
    """CalendarCRUD unit tests — each test uses a fresh in-memory SQLite DB."""

    async def test_create_calendar(self, info_db_session):
        """Create a calendar and verify all fields."""
        cal = _make_calendar()
        created = await calendar_crud.create(info_db_session, cal)

        assert created.id is not None
        assert created.term_code == "2025-2026-1"
        assert created.term_name == "2025-2026学年第一学期"
        assert created.start_date == date(2025, 9, 1)
        assert created.end_date == date(2026, 1, 15)

    async def test_get_calendar(self, info_db_session):
        """Get a calendar by primary key."""
        cal = _make_calendar()
        created = await calendar_crud.create(info_db_session, cal)

        fetched = await calendar_crud.get(info_db_session, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.term_code == "2025-2026-1"

    async def test_get_calendar_not_found(self, info_db_session):
        """Get a non-existent calendar returns None."""
        fetched = await calendar_crud.get(info_db_session, 99999)
        assert fetched is None

    async def test_get_multi_calendars(self, info_db_session):
        """Get paginated calendar list."""
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-1"))
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-2"))

        items = await calendar_crud.get_multi(info_db_session, skip=0, limit=10)
        assert len(items) == 2

    async def test_get_multi_calendars_pagination(self, info_db_session):
        """Get paginated calendar list respects skip/limit."""
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-1"))
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-2"))
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-3"))

        items = await calendar_crud.get_multi(info_db_session, skip=0, limit=2)
        assert len(items) == 2

        items = await calendar_crud.get_multi(info_db_session, skip=2, limit=2)
        assert len(items) == 1

    async def test_update_calendar(self, info_db_session):
        """Update a calendar's fields."""
        cal = _make_calendar()
        created = await calendar_crud.create(info_db_session, cal)

        updated = await calendar_crud.update(
            info_db_session,
            created,
            term_name="更新后的学期名",
            end_date=date(2026, 2, 28),
        )

        assert updated.term_name == "更新后的学期名"
        assert updated.end_date == date(2026, 2, 28)
        assert updated.term_code == "2025-2026-1"  # unchanged

    async def test_delete_calendar(self, info_db_session):
        """Delete a calendar and verify it's gone."""
        cal = _make_calendar()
        created = await calendar_crud.create(info_db_session, cal)

        deleted = await calendar_crud.delete(info_db_session, created.id)
        assert deleted is True

        fetched = await calendar_crud.get(info_db_session, created.id)
        assert fetched is None

    async def test_delete_calendar_not_found(self, info_db_session):
        """Delete a non-existent calendar returns False."""
        deleted = await calendar_crud.delete(info_db_session, 99999)
        assert deleted is False

    async def test_get_by_term_code(self, info_db_session):
        """Get calendar by term_code."""
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-1"))
        await calendar_crud.create(info_db_session, _make_calendar(term_code="2025-2026-2"))

        fetched = await calendar_crud.get_by_term_code(info_db_session, "2025-2026-2")
        assert fetched is not None
        assert fetched.term_code == "2025-2026-2"

    async def test_get_by_term_code_not_found(self, info_db_session):
        """Get calendar by non-existent term_code returns None."""
        fetched = await calendar_crud.get_by_term_code(info_db_session, "nonexistent")
        assert fetched is None

    async def test_get_by_date(self, info_db_session):
        """Get calendar that covers a specific date."""
        await calendar_crud.create(
            info_db_session,
            _make_calendar(
                term_code="2025-2026-1",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 15),
            ),
        )

        fetched = await calendar_crud.get_by_date(info_db_session, date(2025, 10, 15))
        assert fetched is not None
        assert fetched.term_code == "2025-2026-1"

    async def test_get_by_date_boundary_start(self, info_db_session):
        """Get calendar by date on the start boundary."""
        await calendar_crud.create(
            info_db_session,
            _make_calendar(
                term_code="2025-2026-1",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 15),
            ),
        )

        fetched = await calendar_crud.get_by_date(info_db_session, date(2025, 9, 1))
        assert fetched is not None

    async def test_get_by_date_boundary_end(self, info_db_session):
        """Get calendar by date on the end boundary."""
        await calendar_crud.create(
            info_db_session,
            _make_calendar(
                term_code="2025-2026-1",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 15),
            ),
        )

        fetched = await calendar_crud.get_by_date(info_db_session, date(2026, 1, 15))
        assert fetched is not None

    async def test_get_by_date_not_found(self, info_db_session):
        """Get calendar by date outside any range returns None."""
        await calendar_crud.create(
            info_db_session,
            _make_calendar(
                term_code="2025-2026-1",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 15),
            ),
        )

        fetched = await calendar_crud.get_by_date(info_db_session, date(2024, 6, 1))
        assert fetched is None
