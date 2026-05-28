"""Unit tests for schedule CRUD helpers."""

import pytest

from info_service.crud.classroom_crud import classroom_crud
from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.crud.schedule_crud import schedule_crud
from info_service.models.classroom import Classroom
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering
from info_service.models.course_schedule import CourseSchedule


@pytest.mark.unit
class TestScheduleCrud:
    """Verify schedule query and conflict helpers."""

    async def test_get_by_offering_returns_sorted_rows(self, info_db_session) -> None:
        """Schedules for one offering should be returned in weekday/period order."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS801", course_name="Distributed Databases"),
        )
        offering = await offering_crud.create(
            info_db_session,
            CourseOffering(course_id=course.id, term_code="2026-FALL", class_no="01"),
        )
        classroom = await classroom_crud.create(
            info_db_session,
            Classroom(room_no="A-101", building="Main", capacity=80),
        )
        await schedule_crud.create(
            info_db_session,
            CourseSchedule(
                offering_id=offering.id,
                classroom_id=classroom.id,
                day_of_week=3,
                start_period=3,
                end_period=4,
            ),
        )
        await schedule_crud.create(
            info_db_session,
            CourseSchedule(
                offering_id=offering.id,
                classroom_id=classroom.id,
                day_of_week=1,
                start_period=1,
                end_period=2,
            ),
        )
        await info_db_session.commit()

        items = await schedule_crud.get_by_offering(info_db_session, offering.id)

        assert [(item.day_of_week, item.start_period) for item in items] == [(1, 1), (3, 3)]

    async def test_check_conflict_detects_overlapping_periods(self, info_db_session) -> None:
        """Overlapping periods in the same room and weekday should conflict."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS802", course_name="Systems Integration"),
        )
        offering = await offering_crud.create(
            info_db_session,
            CourseOffering(course_id=course.id, term_code="2026-FALL", class_no="01"),
        )
        classroom = await classroom_crud.create(
            info_db_session,
            Classroom(room_no="A-102", building="Main", capacity=60),
        )
        existing = await schedule_crud.create(
            info_db_session,
            CourseSchedule(
                offering_id=offering.id,
                classroom_id=classroom.id,
                day_of_week=2,
                start_period=2,
                end_period=4,
            ),
        )
        await info_db_session.commit()

        assert (
            await schedule_crud.check_conflict(
                info_db_session,
                classroom_id=classroom.id,
                day_of_week=2,
                start_period=4,
                end_period=5,
            )
            is True
        )
        assert (
            await schedule_crud.check_conflict(
                info_db_session,
                classroom_id=classroom.id,
                day_of_week=2,
                start_period=4,
                end_period=5,
                exclude_id=existing.id,
            )
            is False
        )
