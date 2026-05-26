"""Unit tests for CourseManagementService — Calendar methods."""

from datetime import date, datetime

import pytest

from info_service.models.academic_calendar import AcademicCalendar
from info_service.schemas.calendar_schema import (
    CalendarCreateRequest,
    CalendarPatchRequest,
    CalendarUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import ResourceNotFoundError


@pytest.mark.unit
class TestCalendarService:
    """Test calendar business logic using real in-memory DB."""

    async def test_create_calendar(self, info_db_session):
        """Create a calendar via service and verify it's persisted."""
        req = CalendarCreateRequest(
            term_code="2025-2026-1",
            term_name="测试学期",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 15),
        )
        cal = await course_management_service.create_calendar(info_db_session, req)

        assert cal.id is not None
        assert cal.term_code == "2025-2026-1"
        assert cal.term_name == "测试学期"

    async def test_get_calendar(self, info_db_session):
        """Get a calendar by id."""
        req = CalendarCreateRequest(
            term_code="2025-2026-1",
            term_name="测试学期",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 15),
        )
        created = await course_management_service.create_calendar(info_db_session, req)

        fetched = await course_management_service.get_calendar(info_db_session, created.id)
        assert fetched.id == created.id
        assert fetched.term_code == "2025-2026-1"

    async def test_get_calendar_not_found(self, info_db_session):
        """Get a non-existent calendar raises ResourceNotFoundError."""
        with pytest.raises(ResourceNotFoundError):
            await course_management_service.get_calendar(info_db_session, 99999)

    async def test_list_calendars(self, info_db_session):
        """List calendars with pagination."""
        await course_management_service.create_calendar(
            info_db_session,
            CalendarCreateRequest(
                term_code="2025-2026-1",
                term_name="第一学期",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 15),
            ),
        )
        await course_management_service.create_calendar(
            info_db_session,
            CalendarCreateRequest(
                term_code="2025-2026-2",
                term_name="第二学期",
                start_date=date(2026, 2, 15),
                end_date=date(2026, 7, 1),
            ),
        )

        items, total = await course_management_service.list_calendars(
            info_db_session, page=1, page_size=10
        )
        assert len(items) == 2

    async def test_update_calendar(self, info_db_session):
        """Full update a calendar."""
        req = CalendarCreateRequest(
            term_code="2025-2026-1",
            term_name="原始名称",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 15),
        )
        created = await course_management_service.create_calendar(info_db_session, req)

        update_req = CalendarUpdateRequest(
            term_code="2025-2026-1-UPDATED",
            term_name="更新后名称",
            start_date=date(2025, 9, 15),
            end_date=date(2026, 2, 1),
        )
        updated = await course_management_service.update_calendar(
            info_db_session, created.id, update_req
        )

        assert updated.term_code == "2025-2026-1-UPDATED"
        assert updated.term_name == "更新后名称"
        assert updated.start_date == date(2025, 9, 15)

    async def test_patch_calendar(self, info_db_session):
        """Partial update only changes provided fields."""
        req = CalendarCreateRequest(
            term_code="2025-2026-1",
            term_name="原始名称",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 15),
        )
        created = await course_management_service.create_calendar(info_db_session, req)

        patch_req = CalendarPatchRequest(term_name="补丁更新名称")
        patched = await course_management_service.patch_calendar(
            info_db_session, created.id, patch_req
        )

        assert patched.term_name == "补丁更新名称"
        assert patched.term_code == "2025-2026-1"  # unchanged

    async def test_delete_calendar(self, info_db_session):
        """Delete a calendar and verify it's gone."""
        req = CalendarCreateRequest(
            term_code="2025-2026-1",
            term_name="测试学期",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 15),
        )
        created = await course_management_service.create_calendar(info_db_session, req)

        await course_management_service.delete_calendar(info_db_session, created.id)

        with pytest.raises(ResourceNotFoundError):
            await course_management_service.get_calendar(info_db_session, created.id)

    async def test_get_calendar_by_term(self, info_db_session):
        """Get calendar by term_code."""
        await course_management_service.create_calendar(
            info_db_session,
            CalendarCreateRequest(
                term_code="2025-2026-1",
                term_name="第一学期",
                start_date=date(2025, 9, 1),
                end_date=date(2026, 1, 15),
            ),
        )

        cal = await course_management_service.get_calendar_by_term(
            info_db_session, "2025-2026-1"
        )
        assert cal is not None
        assert cal.term_code == "2025-2026-1"

    async def test_get_calendar_by_term_not_found(self, info_db_session):
        """Get calendar by non-existent term_code returns None."""
        cal = await course_management_service.get_calendar_by_term(
            info_db_session, "nonexistent"
        )
        assert cal is None
