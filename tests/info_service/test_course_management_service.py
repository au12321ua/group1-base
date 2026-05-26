"""Unit tests for course management service behavior."""

from unittest.mock import AsyncMock

import pytest

from info_service.crud.course_crud import course_crud
from info_service.crud.offering_crud import offering_crud
from info_service.models.course import Course
from info_service.models.course_offering import CourseOffering
from info_service.schemas.offering_schema import OfferingPatchRequest
from info_service.services.course_management_service import course_management_service


@pytest.mark.unit
class TestCourseManagementService:
    """Verify service-layer orchestration for offering updates."""

    async def test_update_offering_skips_identity_check_when_identity_unchanged(
        self, info_db_session, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Updating non-identity fields should not re-run duplicate identity validation."""
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
                teacher_ids="t-1",
                status="ACTIVE",
            ),
        )
        await info_db_session.commit()

        identity_check = AsyncMock()
        monkeypatch.setattr(
            course_management_service,
            "_ensure_unique_offering_identity",
            identity_check,
        )

        updated = await course_management_service.update_offering(
            info_db_session,
            offering.id,
            OfferingPatchRequest(teacher_ids=["t-2", "t-3"], status="COMPLETED"),
        )

        identity_check.assert_not_awaited()
        assert updated.teacher_ids == "t-2,t-3"
        assert updated.status == "COMPLETED"
