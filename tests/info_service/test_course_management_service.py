"""Unit tests for course management service behavior."""

from unittest.mock import AsyncMock

import pytest

from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering
from info_service.schemas.offering_schema import OfferingPatchRequest
from info_service.services.course_management_service import course_management_service
from shared.exceptions import ResourceNotFoundError


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
