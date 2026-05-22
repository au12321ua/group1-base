"""Unit tests for course CRUD and prerequisite relations."""

import pytest

from info_service.crud.course_crud import course_crud
from info_service.models.course import Course
from shared.exceptions import BusinessRuleError


@pytest.mark.unit
class TestCourseCrud:
    """Verify course CRUD behavior in isolation."""

    async def test_get_by_course_code_returns_created_course(self, info_db_session):
        """Should fetch a course by its unique course_code."""
        created = await course_crud.create(
            info_db_session,
            Course(course_code="CS101", course_name="Intro to CS", credit=3, capacity=120),
        )
        await info_db_session.commit()

        found = await course_crud.get_by_course_code(info_db_session, "CS101")

        assert found is not None
        assert found.id == created.id
        assert found.course_name == "Intro to CS"

    async def test_get_multi_filters_keyword_and_excludes_deleted_by_default(self, info_db_session):
        """Default listing hides logically deleted courses and supports keyword search."""
        course_1 = await course_crud.create(
            info_db_session,
            Course(course_code="CS101", course_name="Computer Science Basics", is_active=True),
        )
        await course_crud.create(
            info_db_session,
            Course(course_code="MATH201", course_name="Linear Algebra", is_active=False),
        )
        course_3 = await course_crud.create(
            info_db_session,
            Course(course_code="CS301", course_name="Advanced Systems", is_active=True),
        )
        await info_db_session.commit()

        await course_crud.logical_delete(info_db_session, course_3.id)
        await info_db_session.commit()

        items, total = await course_crud.get_multi(
            info_db_session,
            keyword="CS",
            is_active=True,
        )

        assert total == 1
        assert [item.course_code for item in items] == ["CS101"]
        assert course_1.id == items[0].id

    async def test_logical_delete_marks_course_deleted_and_inactive(self, info_db_session):
        """Logical delete should mark the course deleted instead of removing the row."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="PHY101", course_name="Physics", is_active=True),
        )
        await info_db_session.commit()

        await course_crud.logical_delete(info_db_session, course.id)
        await info_db_session.commit()

        deleted = await course_crud.get(info_db_session, course.id)
        visible_items, visible_total = await course_crud.get_multi(info_db_session)
        all_items, all_total = await course_crud.get_multi(info_db_session, include_deleted=True)

        assert deleted is not None
        assert deleted.is_deleted is True
        assert deleted.is_active is False
        assert visible_total == 0
        assert visible_items == []
        assert all_total == 1
        assert all_items[0].id == course.id

    async def test_can_add_list_and_remove_prerequisite(self, info_db_session):
        """Should maintain prerequisite relations between two courses."""
        target = await course_crud.create(
            info_db_session,
            Course(course_code="CS201", course_name="Data Structures"),
        )
        prerequisite = await course_crud.create(
            info_db_session,
            Course(course_code="CS101", course_name="Intro to CS"),
        )
        await info_db_session.commit()

        relation = await course_crud.add_prerequisite(
            info_db_session,
            course_id=target.id,
            prerequisite_course_id=prerequisite.id,
            min_grade="C",
        )
        await info_db_session.commit()

        relations = await course_crud.list_prerequisites(info_db_session, target.id)
        removed = await course_crud.remove_prerequisite(
            info_db_session,
            course_id=target.id,
            prerequisite_course_id=prerequisite.id,
        )
        await info_db_session.commit()

        assert relation.course_id == target.id
        assert relation.prerequisite_course_id == prerequisite.id
        assert relation.min_grade == "C"
        assert len(relations) == 1
        assert relations[0].id == relation.id
        assert removed is True
        assert await course_crud.list_prerequisites(info_db_session, target.id) == []

    async def test_add_prerequisite_rejects_self_reference(self, info_db_session):
        """A course cannot list itself as its own prerequisite."""
        course = await course_crud.create(
            info_db_session,
            Course(course_code="CS999", course_name="Impossible Course"),
        )
        await info_db_session.commit()

        with pytest.raises(BusinessRuleError):
            await course_crud.add_prerequisite(
                info_db_session,
                course_id=course.id,
                prerequisite_course_id=course.id,
            )
