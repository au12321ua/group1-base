"""Unit tests for classroom CRUD helpers."""

import pytest

from info_service.crud.classroom_crud import classroom_crud
from info_service.models.classroom import Classroom


@pytest.mark.unit
class TestClassroomCrud:
    """Verify classroom CRUD query helpers."""

    async def test_get_by_room_no_returns_classroom(self, info_db_session):
        """Should fetch classroom by its unique room number."""
        created = await classroom_crud.create(
            info_db_session,
            Classroom(room_no="A-101", building="Main", capacity=80, type="standard"),
        )
        await info_db_session.commit()

        found = await classroom_crud.get_by_room_no(info_db_session, "A-101")

        assert found is not None
        assert found.id == created.id
        assert found.building == "Main"

    async def test_get_multi_applies_filters(self, info_db_session):
        """Should filter classrooms by building, type, capacity, and keyword."""
        await classroom_crud.create(
            info_db_session,
            Classroom(room_no="A-101", building="Main", capacity=80, type="standard"),
        )
        await classroom_crud.create(
            info_db_session,
            Classroom(room_no="A-202", building="Main", capacity=150, type="lecture_hall"),
        )
        await classroom_crud.create(
            info_db_session,
            Classroom(room_no="B-303", building="Lab", capacity=40, type="lab"),
        )
        await info_db_session.commit()

        items, total = await classroom_crud.get_multi(
            info_db_session,
            keyword="A-",
            building="Main",
            classroom_type="lecture_hall",
            min_capacity=100,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].room_no == "A-202"

    async def test_delete_removes_classroom_row(self, info_db_session):
        """Physical delete should remove the classroom row entirely."""
        created = await classroom_crud.create(
            info_db_session,
            Classroom(room_no="C-404", building="North", capacity=60, type="standard"),
        )
        await info_db_session.commit()

        deleted = await classroom_crud.delete(info_db_session, created.id)
        await info_db_session.commit()

        assert deleted is True
        assert await classroom_crud.get(info_db_session, created.id) is None
