"""Integration tests for /api/v1/data-provision endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from info_service.main import info_engine
from info_service.models.academic_calendar import AcademicCalendar
from info_service.models.training_program import TrainingProgram
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.services.data_provision_service import data_provision_service
from tests.utils import build_identity_headers


async def _seed_user(
    *,
    user_no: str,
    username: str,
    role_ids: str,
    full_name: str,
    status: str = "ACTIVE",
) -> None:
    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        user = UserInfo(user_no=user_no, username=username, role_ids=role_ids)
        session.add(user)
        await session.flush()
        session.add(
            UserProfile(
                user_id=user.id,
                full_name=full_name,
                email=f"{username}@test.com",
                phone="13800000000",
                status=status,
            )
        )
        await session.commit()


async def _seed_calendar(*, term_code: str, term_name: str, snapshot_time: datetime) -> None:
    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        session.add(
            AcademicCalendar(
                term_code=term_code,
                term_name=term_name,
                start_date=datetime(2026, 9, 1, tzinfo=UTC).date(),
                end_date=datetime(2027, 1, 15, tzinfo=UTC).date(),
                version="1.0",
                snapshot_time=snapshot_time,
            )
        )
        await session.commit()


async def _seed_training_program(
    *,
    program_code: str,
    major_code: str,
    grade: str,
    version: str,
    required_course_ids: str,
    snapshot_time: datetime,
) -> None:
    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        session.add(
            TrainingProgram(
                program_code=program_code,
                major_code=major_code,
                grade=grade,
                version=version,
                required_course_ids=required_course_ids,
                snapshot_time=snapshot_time,
            )
        )
        await session.commit()


async def _cleanup_table(table) -> None:
    from sqlmodel import delete

    async with AsyncSession(info_engine, expire_on_commit=False) as session:
        await session.exec(delete(table))
        await session.commit()


@pytest.mark.integration
class TestDataProvisionAPI:
    """Verify the data provision endpoints used by downstream systems."""

    @pytest.fixture
    def auth_headers(self) -> dict[str, str]:
        return build_identity_headers()

    async def test_list_teachers_and_candidate_students(
        self, async_client_info, auth_headers
    ) -> None:
        """Should return paginated teachers and candidate students with snapshot metadata."""
        await _seed_user(
            user_no="T1001",
            username="teacher_api",
            role_ids="2",
            full_name="Teacher API",
        )
        await _seed_user(
            user_no="20230001",
            username="student_api",
            role_ids="1",
            full_name="Student API",
        )

        teacher_resp = await async_client_info.get(
            "/api/v1/data-provision/teachers",
            params={"page": 1, "page_size": 20},
            headers=auth_headers,
        )
        assert teacher_resp.status_code == 200
        teacher_data = teacher_resp.json()["data"]
        assert teacher_data["pagination"] == {"total": 1, "page": 1, "page_size": 20}
        assert teacher_data["items"][0]["username"] == "teacher_api"
        assert teacher_data["snapshot_time"]

        student_resp = await async_client_info.get(
            "/api/v1/data-provision/candidate-students",
            params={"page": 1, "page_size": 20},
            headers=auth_headers,
        )
        assert student_resp.status_code == 200
        student_data = student_resp.json()["data"]
        assert student_data["pagination"] == {"total": 1, "page": 1, "page_size": 20}
        assert student_data["items"][0]["username"] == "student_api"
        assert student_data["items"][0]["grade"] == "2023"
        assert student_data["snapshot_time"]

        await _cleanup_table(UserProfile)
        await _cleanup_table(UserInfo)

    async def test_get_calendars(self, async_client_info, auth_headers) -> None:
        """Should expose calendar snapshots with top-level snapshot metadata."""
        await _seed_calendar(
            term_code="2026-FALL",
            term_name="2026 Fall",
            snapshot_time=datetime(2026, 8, 1, tzinfo=UTC),
        )
        await _seed_calendar(
            term_code="2027-SPRING",
            term_name="2027 Spring",
            snapshot_time=datetime(2026, 12, 1, tzinfo=UTC),
        )

        resp = await async_client_info.get(
            "/api/v1/data-provision/calendars", headers=auth_headers
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["pagination"] == {"total": 2, "page": 1, "page_size": 2}
        assert [item["term_code"] for item in data["items"]] == ["2026-FALL", "2027-SPRING"]
        assert data["snapshot_time"] == "2026-12-01T00:00:00Z"

        await _cleanup_table(AcademicCalendar)

    async def test_get_calendars_empty(self, async_client_info, auth_headers) -> None:
        """Should return empty items with fallback snapshot and pagination."""
        resp = await async_client_info.get(
            "/api/v1/data-provision/calendars", headers=auth_headers
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["items"] == []
        assert data["pagination"] == {"total": 0, "page": 1, "page_size": 0}
        assert data["version"] == "1.0"
        assert data["snapshot_time"]  # should be a fallback datetime

    async def test_list_training_programs_supports_filters(
        self, async_client_info, auth_headers
    ) -> None:
        """Should return normalized training program snapshots and filter by query params."""
        await _seed_training_program(
            program_code="CS-2026-V1",
            major_code="CS",
            grade="2026",
            version="1.0",
            required_course_ids="1,2,3",
            snapshot_time=datetime(2026, 4, 1, tzinfo=UTC),
        )
        await _seed_training_program(
            program_code="EE-2026-V1",
            major_code="EE",
            grade="2026",
            version="1.0",
            required_course_ids="4,5",
            snapshot_time=datetime(2026, 4, 2, tzinfo=UTC),
        )

        resp = await async_client_info.get(
            "/api/v1/data-provision/training-programs",
            params={
                "page": 1,
                "page_size": 10,
                "major_code": "CS",
                "grade": "2026",
                "version": "1.0",
            },
            headers=auth_headers,
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["pagination"] == {"total": 1, "page": 1, "page_size": 10}
        assert data["version"] == "1.0"
        assert data["items"][0]["program_code"] == "CS-2026-V1"
        assert data["items"][0]["required_course_ids"] == [1, 2, 3]
        assert data["snapshot_time"] == "2026-04-01T00:00:00Z"

        await _cleanup_table(TrainingProgram)

    async def test_query_selected_students_proxies_normalized_payload(
        self,
        async_client_info,
        auth_headers,
    ) -> None:
        """Should return the normalized selected student payload from the proxy service."""
        with patch.object(
            data_provision_service,
            "query_selected_students",
            new=AsyncMock(
                return_value={
                    "items": [{"student_id": "s-1", "course_id": 1001}],
                    "pagination": {"total": 1, "page": 1, "page_size": 20},
                    "snapshot_time": datetime(2026, 5, 30, tzinfo=UTC),
                    "version": "2.0",
                }
            ),
        ):
            resp = await async_client_info.get(
                "/api/v1/data-provision/selected-students",
                params={"course_id": 1001, "term_code": "2026-FALL", "page_size": 20},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["items"] == [{"student_id": "s-1", "course_id": 1001}]
        assert data["pagination"] == {"total": 1, "page": 1, "page_size": 20}
        assert data["version"] == "2.0"
        assert data["snapshot_time"] == "2026-05-30T00:00:00Z"
