"""Unit tests for DataProvisionService."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from info_service.models.training_program import TrainingProgram
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.services.data_provision_service import data_provision_service


async def _create_user(
    db,
    *,
    user_no: str,
    username: str,
    role_ids: str,
    full_name: str,
    status: str = "ACTIVE",
    is_deleted: bool = False,
) -> None:
    user = UserInfo(
        user_no=user_no,
        username=username,
        role_ids=role_ids,
        is_deleted=is_deleted,
    )
    db.add(user)
    await db.flush()
    db.add(
        UserProfile(
            user_id=user.id,
            full_name=full_name,
            email=f"{username}@test.com",
            phone="13800000000",
            status=status,
        )
    )
    await db.flush()


@pytest.mark.unit
class TestDataProvisionService:
    """DataProvisionService unit tests."""

    async def test_list_teachers_and_candidate_students_filter_by_role_and_status(
        self,
        info_db_session,
    ) -> None:
        """Should only expose active, non-deleted users for the requested role."""
        await _create_user(
            info_db_session,
            user_no="T001",
            username="teacher_1",
            role_ids="2",
            full_name="Teacher One",
        )
        await _create_user(
            info_db_session,
            user_no="20240001",
            username="student_1",
            role_ids="1",
            full_name="Student One",
        )
        await _create_user(
            info_db_session,
            user_no="T002",
            username="teacher_disabled",
            role_ids="2",
            full_name="Disabled Teacher",
            status="DISABLED",
        )
        await _create_user(
            info_db_session,
            user_no="20240002",
            username="student_deleted",
            role_ids="1",
            full_name="Deleted Student",
            is_deleted=True,
        )

        teachers, teacher_total = await data_provision_service.list_teachers(
            info_db_session,
            page=1,
            page_size=10,
        )
        students, student_total = await data_provision_service.list_candidate_students(
            info_db_session,
            page=1,
            page_size=10,
        )

        assert teacher_total == 1
        assert [item.username for item in teachers] == ["teacher_1"]
        assert teachers[0].full_name == "Teacher One"

        assert student_total == 1
        assert [item.username for item in students] == ["student_1"]
        assert students[0].grade == "2024"

    async def test_list_training_programs_parses_required_course_ids(
        self,
        info_db_session,
    ) -> None:
        """Should convert stored comma-separated course ids into integer lists."""
        info_db_session.add(
            TrainingProgram(
                program_code="CS-2026-V1",
                major_code="CS",
                grade="2026",
                version="1.0",
                required_course_ids="1, 2, x, 3",
                snapshot_time=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        info_db_session.add(
            TrainingProgram(
                program_code="EE-2026-V1",
                major_code="EE",
                grade="2026",
                version="1.0",
                required_course_ids="4,5",
                snapshot_time=datetime(2026, 1, 2, tzinfo=UTC),
            )
        )
        await info_db_session.flush()

        items, total = await data_provision_service.list_training_programs(
            info_db_session,
            page=1,
            page_size=10,
            major_code="CS",
        )

        assert total == 1
        assert items[0].program_code == "CS-2026-V1"
        assert items[0].required_course_ids == [1, 2, 3]

    async def test_query_selected_students_normalizes_api_response_payload(
        self,
        info_db_session,
    ) -> None:
        """Should accept the standard APIResponse envelope returned by C service."""
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "code": 0,
            "message": "success",
            "data": {
                "items": [{"student_id": "s-1"}],
                "pagination": {"total": 1, "page": 1, "page_size": 50},
                "snapshot_time": "2026-05-30T00:00:00Z",
                "version": "2.0",
            },
        }

        client = MagicMock()
        client.get = AsyncMock(return_value=response)
        client_cm = MagicMock()
        client_cm.__aenter__ = AsyncMock(return_value=client)
        client_cm.__aexit__ = AsyncMock(return_value=None)

        with patch(
            "info_service.services.data_provision_service.httpx.AsyncClient",
            return_value=client_cm,
        ):
            payload = await data_provision_service.query_selected_students(
                info_db_session,
                course_id=101,
                page=1,
                page_size=50,
            )

        assert payload["items"] == [{"student_id": "s-1"}]
        assert payload["pagination"] == {"total": 1, "page": 1, "page_size": 50}
        assert payload["version"] == "2.0"
        assert payload["snapshot_time"] == datetime(2026, 5, 30, tzinfo=UTC)
