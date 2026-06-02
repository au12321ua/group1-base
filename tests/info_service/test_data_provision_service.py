"""Unit tests for DataProvisionService."""

from datetime import UTC, datetime

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
    full_name: str,
    status: str = "ACTIVE",
    is_deleted: bool = False,
) -> None:
    user = UserInfo(
        user_no=user_no,
        username=username,
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
            full_name="Teacher One",
        )
        await _create_user(
            info_db_session,
            user_no="20240001",
            username="student_1",
            full_name="Student One",
        )
        await _create_user(
            info_db_session,
            user_no="T002",
            username="teacher_disabled",
            full_name="Disabled Teacher",
            status="DISABLED",
        )
        await _create_user(
            info_db_session,
            user_no="20240002",
            username="student_deleted",
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

        # Role filtering removed — all active users are returned
        assert teacher_total == 2
        assert {item.username for item in teachers} == {"teacher_1", "student_1"}

        assert student_total == 2
        assert {item.username for item in students} == {"teacher_1", "student_1"}

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
                snapshot_time=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        info_db_session.add(
            TrainingProgram(
                program_code="EE-2026-V1",
                major_code="EE",
                grade="2026",
                version="1.0",
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
        assert items[0].required_course_ids == []

    async def test_list_teachers_uses_default_pagination(
        self, info_db_session,
    ) -> None:
        """Should default to page=1, page_size=100 when not specified."""
        # Seed multiple teachers
        for i in range(3):
            await _create_user(
                info_db_session,
                user_no=f"T00{i}",
                username=f"teacher_paginate_{i}",
                full_name=f"Teacher Paginate {i}",
            )

        items, total = await data_provision_service.list_teachers(info_db_session)

        assert total == 3
        assert len(items) == 3  # all fit within default page_size=100
