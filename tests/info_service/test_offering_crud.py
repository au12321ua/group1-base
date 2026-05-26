"""Unit tests for offering CRUD helpers."""

import pytest

from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering


@pytest.mark.unit
class TestOfferingCrud:
    """Verify offering queries and persistence behavior."""

    async def test_get_by_course_and_term_returns_matching_rows(self, info_db_session):
        """Should return offerings for the same course and term in id order."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS201", course_name="Data Structures"),
        )
        other_course = await course_crud.create(
            info_db_session,
            Course(course_code="CS202", course_name="Algorithms"),
        )
        await offering_crud.create(
            info_db_session,
            CourseOffering(course_id=course.id, term_code="2026-FALL", class_no="01"),
        )
        second = await offering_crud.create(
            info_db_session,
            CourseOffering(course_id=course.id, term_code="2026-FALL", class_no="02"),
        )
        await offering_crud.create(
            info_db_session,
            CourseOffering(course_id=other_course.id, term_code="2026-FALL", class_no="01"),
        )
        await info_db_session.commit()

        items = await offering_crud.get_by_course_and_term(info_db_session, course.id, "2026-FALL")

        assert [item.class_no for item in items] == ["01", "02"]
        assert items[1].id == second.id

    async def test_get_multi_applies_supported_filters(self, info_db_session):
        """Should filter by course, term, and status."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS301", course_name="Operating Systems"),
        )
        other_course = await course_crud.create(
            info_db_session,
            Course(course_code="CS302", course_name="Networks"),
        )
        await offering_crud.create(
            info_db_session,
            CourseOffering(
                course_id=course.id,
                term_code="2026-FALL",
                class_no="01",
                status="ACTIVE",
            ),
        )
        await offering_crud.create(
            info_db_session,
            CourseOffering(
                course_id=course.id,
                term_code="2026-SPRING",
                class_no="01",
                status="CANCELLED",
            ),
        )
        await offering_crud.create(
            info_db_session,
            CourseOffering(
                course_id=other_course.id,
                term_code="2026-FALL",
                class_no="01",
                status="ACTIVE",
            ),
        )
        await info_db_session.commit()

        items, total = await offering_crud.get_multi(
            info_db_session,
            course_id=course.id,
            term_code="2026-FALL",
            status="ACTIVE",
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].course_id == course.id
        assert items[0].term_code == "2026-FALL"

    async def test_delete_removes_offering_row(self, info_db_session):
        """Physical delete should remove the offering row entirely."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS401", course_name="Compilers"),
        )
        offering = await offering_crud.create(
            info_db_session,
            CourseOffering(course_id=course.id, term_code="2026-FALL", class_no="01"),
        )
        await info_db_session.commit()

        deleted = await offering_crud.delete(info_db_session, offering.id)
        await info_db_session.commit()

        assert deleted is True
        assert await offering_crud.get(info_db_session, offering.id) is None
