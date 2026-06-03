"""Unit tests for course management service behavior."""

from unittest.mock import AsyncMock

import pytest

from info_service.crud.classroom_crud import classroom_crud
from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.crud.schedule_crud import schedule_crud
from info_service.models.classroom import Classroom
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering
from info_service.models.course_schedule import CourseSchedule
from info_service.schemas.course_schema import CourseCreateRequest, CoursePatchRequest
from info_service.schemas.offering_schema import OfferingPatchRequest
from info_service.schemas.schedule_schema import ScheduleCreateRequest, SchedulePatchRequest
from info_service.services.course_management_service import course_management_service
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


async def _create_course(
    db,
    *,
    course_code: str,
    course_name: str,
) -> Course:
    return await course_crud.create(
        db,
        Course(course_code=course_code, course_name=course_name),
    )


async def _create_offering(
    db,
    *,
    course_id: int,
    class_no: str = "01",
) -> CourseOffering:
    return await offering_crud.create(
        db,
        CourseOffering(course_id=course_id, term_code="2026-FALL", class_no=class_no),
    )


async def _create_classroom(
    db,
    *,
    room_no: str,
) -> Classroom:
    return await classroom_crud.create(
        db,
        Classroom(room_no=room_no, building="Main", capacity=80, type="standard"),
    )


async def _create_schedule(
    db,
    *,
    offering_id: int,
    classroom_id: int,
    day_of_week: int,
    start_period: int,
    end_period: int,
) -> CourseSchedule:
    return await schedule_crud.create(
        db,
        CourseSchedule(
            offering_id=offering_id,
            classroom_id=classroom_id,
            day_of_week=day_of_week,
            start_period=start_period,
            end_period=end_period,
        ),
    )


@pytest.mark.unit
class TestCourseManagementService:
    """Verify service-layer orchestration for course domain updates."""

    async def test_update_offering_updates_non_identity_fields(
        self, info_db_session
    ) -> None:
        """Updating non-identity fields (e.g. status, capacity) should succeed
        without triggering a uniqueness violation.

        Uniqueness of (course_id, term_code, class_no) is enforced at the
        database level via UniqueConstraint — no service-layer check needed.
        """
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS701", course_name="Service Test Course"),
        )
        offering = await offering_crud.create(
            info_db_session,
            CourseOffering(
                course_id=course.id,
                term_code="2026-FALL",
                class_no="01",
                status="ACTIVE",
            ),
        )
        await info_db_session.commit()

        updated = await course_management_service.update_offering(
            info_db_session,
            offering.id,
            OfferingPatchRequest(status="COMPLETED"),
        )

        assert updated.status == "COMPLETED"
        assert updated.term_code == "2026-FALL"
        assert updated.class_no == "01"

    async def test_ensure_required_courses_exist_uses_bulk_lookup(
        self, info_db_session, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Required course validation should use one bulk lookup and preserve errors."""
        existing_ids_lookup = AsyncMock(return_value={1, 3})
        monkeypatch.setattr(course_crud, "get_existing_ids", existing_ids_lookup)

        with pytest.raises(ResourceNotFoundError):
            await course_management_service._ensure_required_courses_exist(
                info_db_session,
                [1, 2, 3],
            )

        existing_ids_lookup.assert_awaited_once_with(info_db_session, [1, 2, 3])

    async def test_create_course_rejects_duplicate_code(self, info_db_session) -> None:
        """Creating a second course with the same course_code should fail."""
        await course_management_service.create_course(
            info_db_session,
            CourseCreateRequest(course_code="CS710", course_name="First Course"),
        )

        with pytest.raises(BusinessRuleError, match="Course code already exists"):
            await course_management_service.create_course(
                info_db_session,
                CourseCreateRequest(course_code="CS710", course_name="Duplicate Course"),
            )

    async def test_update_course_rejects_duplicate_code(self, info_db_session) -> None:
        """Updating a course to another course's code should fail."""
        first = await _create_course(
            info_db_session,
            course_code="CS711",
            course_name="First Course",
        )
        second = await _create_course(
            info_db_session,
            course_code="CS712",
            course_name="Second Course",
        )

        with pytest.raises(BusinessRuleError, match="Course code already exists"):
            await course_management_service.update_course(
                info_db_session,
                second.id,
                CoursePatchRequest(course_code=first.course_code),
            )

    async def test_create_schedule_rejects_conflict(self, info_db_session) -> None:
        """Creating an overlapping schedule in the same room and weekday should fail."""
        course = await _create_course(
            info_db_session,
            course_code="CS713",
            course_name="Conflict Course",
        )
        offering = await _create_offering(info_db_session, course_id=course.id)
        classroom = await _create_classroom(info_db_session, room_no="SVC-101")
        await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=2,
            start_period=3,
            end_period=4,
        )

        with pytest.raises(BusinessRuleError, match="Schedule conflicts"):
            await course_management_service.create_schedule(
                info_db_session,
                ScheduleCreateRequest(
                    offering_id=offering.id,
                    classroom_id=classroom.id,
                    day_of_week=2,
                    start_period=4,
                    end_period=5,
                    week_range="1-16",
                ),
            )

    async def test_update_schedule_rejects_conflict_when_identity_changes(
        self, info_db_session
    ) -> None:
        """Changing a schedule into an occupied period should fail conflict validation."""
        course = await _create_course(
            info_db_session,
            course_code="CS714",
            course_name="Schedule Update Conflict",
        )
        offering = await _create_offering(info_db_session, course_id=course.id)
        classroom = await _create_classroom(info_db_session, room_no="SVC-102")
        existing = await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=3,
            start_period=5,
            end_period=6,
        )
        target = await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=3,
            start_period=8,
            end_period=9,
        )

        with pytest.raises(BusinessRuleError, match="Schedule conflicts"):
            await course_management_service.update_schedule(
                info_db_session,
                target.id,
                SchedulePatchRequest(start_period=6, end_period=7),
            )

        assert existing.id != target.id

    async def test_delete_schedule_not_found_raises(self, info_db_session) -> None:
        """Deleting a missing schedule should raise ResourceNotFoundError."""
        with pytest.raises(ResourceNotFoundError):
            await course_management_service.delete_schedule(info_db_session, 99999)

    async def test_replace_teachers_normalizes_and_replaces_existing_assignments(
        self, info_db_session
    ) -> None:
        """Replacing teachers should strip whitespace, deduplicate IDs, and drop stale rows."""
        course = await _create_course(
            info_db_session,
            course_code="CS715",
            course_name="Teacher Replace",
        )
        offering = await _create_offering(info_db_session, course_id=course.id)
        classroom = await _create_classroom(info_db_session, room_no="SVC-103")
        schedule = await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=1,
            start_period=1,
            end_period=2,
        )
        await course_management_service.assign_teacher(
            info_db_session,
            schedule.id,
            "legacy-teacher",
            "assistant",
        )

        replaced = await course_management_service.replace_teachers(
            info_db_session,
            schedule.id,
            [" t-1 ", "t-2", "t-1", ""],
        )

        assert [item.teacher_id for item in replaced] == ["t-1", "t-2"]
        persisted = await course_management_service.list_teachers_for_schedule(
            info_db_session,
            schedule.id,
        )
        assert [item.teacher_id for item in persisted] == ["t-1", "t-2"]

    async def test_add_teachers_deduplicates_existing_assignments(
        self, info_db_session
    ) -> None:
        """Adding teachers should keep existing assignments and ignore duplicates/blanks."""
        course = await _create_course(
            info_db_session,
            course_code="CS716",
            course_name="Teacher Add",
        )
        offering = await _create_offering(info_db_session, course_id=course.id)
        classroom = await _create_classroom(info_db_session, room_no="SVC-104")
        schedule = await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=4,
            start_period=3,
            end_period=4,
        )
        await course_management_service.assign_teacher(
            info_db_session,
            schedule.id,
            "t-1",
            "instructor",
        )

        items = await course_management_service.add_teachers(
            info_db_session,
            schedule.id,
            [" t-1 ", "t-2", "", "t-2"],
        )

        assert [item.teacher_id for item in items] == ["t-1", "t-2"]

    async def test_assign_teacher_updates_existing_role(self, info_db_session) -> None:
        """Assigning the same teacher again should update role_type in place."""
        course = await _create_course(
            info_db_session,
            course_code="CS717",
            course_name="Teacher Assign",
        )
        offering = await _create_offering(info_db_session, course_id=course.id)
        classroom = await _create_classroom(info_db_session, room_no="SVC-105")
        schedule = await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=5,
            start_period=7,
            end_period=8,
        )

        created = await course_management_service.assign_teacher(
            info_db_session,
            schedule.id,
            "t-9",
            "instructor",
        )
        updated = await course_management_service.assign_teacher(
            info_db_session,
            schedule.id,
            " t-9 ",
            "assistant",
        )

        assert created.id == updated.id
        assert updated.role_type == "assistant"

    async def test_remove_teacher_not_found_raises(self, info_db_session) -> None:
        """Removing a missing teacher assignment should raise ResourceNotFoundError."""
        course = await _create_course(
            info_db_session,
            course_code="CS718",
            course_name="Teacher Remove",
        )
        offering = await _create_offering(info_db_session, course_id=course.id)
        classroom = await _create_classroom(info_db_session, room_no="SVC-106")
        schedule = await _create_schedule(
            info_db_session,
            offering_id=offering.id,
            classroom_id=classroom.id,
            day_of_week=2,
            start_period=9,
            end_period=10,
        )

        with pytest.raises(ResourceNotFoundError):
            await course_management_service.remove_teacher(
                info_db_session,
                schedule.id,
                "missing-teacher",
            )
