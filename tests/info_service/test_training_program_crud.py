"""Unit tests for training program CRUD helpers."""

import pytest

from info_service.crud.training_program_crud import training_program_crud
from info_service.models.training_program import TrainingProgram


@pytest.mark.unit
class TestTrainingProgramCrud:
    """Verify training program query helpers."""

    async def test_get_by_program_code_returns_program(self, info_db_session):
        """Should fetch a training program by its unique program code."""
        created = await training_program_crud.create(
            info_db_session,
            TrainingProgram(
                program_code="SE-2026",
                major_code="SE",
                grade="2026",
                required_course_ids="1,2,3",
            ),
        )
        await info_db_session.commit()

        found = await training_program_crud.get_by_program_code(info_db_session, "SE-2026")

        assert found is not None
        assert found.id == created.id
        assert found.major_code == "SE"

    async def test_get_by_major_can_filter_grade(self, info_db_session):
        """Should list training programs by major and optional grade."""
        await training_program_crud.create(
            info_db_session,
            TrainingProgram(program_code="CS-2025", major_code="CS", grade="2025"),
        )
        second = await training_program_crud.create(
            info_db_session,
            TrainingProgram(program_code="CS-2026", major_code="CS", grade="2026"),
        )
        await training_program_crud.create(
            info_db_session,
            TrainingProgram(program_code="EE-2026", major_code="EE", grade="2026"),
        )
        await info_db_session.commit()

        items = await training_program_crud.get_by_major(info_db_session, "CS", "2026")

        assert len(items) == 1
        assert items[0].id == second.id

    async def test_get_multi_applies_filters(self, info_db_session):
        """Should support paginated filtering by major, grade, and version."""
        await training_program_crud.create(
            info_db_session,
            TrainingProgram(
                program_code="AI-2026-V1",
                major_code="AI",
                grade="2026",
                version="1.0",
            ),
        )
        await training_program_crud.create(
            info_db_session,
            TrainingProgram(
                program_code="AI-2026-V2",
                major_code="AI",
                grade="2026",
                version="2.0",
            ),
        )
        await training_program_crud.create(
            info_db_session,
            TrainingProgram(
                program_code="AI-2025-V1",
                major_code="AI",
                grade="2025",
                version="1.0",
            ),
        )
        await info_db_session.commit()

        items, total = await training_program_crud.get_multi(
            info_db_session,
            major_code="AI",
            grade="2026",
            version="2.0",
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].program_code == "AI-2026-V2"
