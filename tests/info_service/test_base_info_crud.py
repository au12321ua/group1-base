"""Unit tests for BaseInfoCRUD."""

import pytest

from info_service.crud.base_info_crud import base_info_crud
from info_service.models.base_info_item import BaseInfoItem


def _make_item(**overrides) -> BaseInfoItem:
    """Create a BaseInfoItem instance with default test values."""
    defaults = {
        "category": "department",
        "item_code": "CS",
        "item_name": "计算机科学系",
        "description": "计算机科学与技术系",
        "is_active": True,
    }
    defaults.update(overrides)
    return BaseInfoItem(**defaults)


@pytest.mark.unit
class TestBaseInfoCRUD:
    """BaseInfoCRUD unit tests — each test uses a fresh in-memory SQLite DB."""

    async def test_create_base_info(self, info_db_session):
        """Create a base info item and verify all fields."""
        item = _make_item()
        created = await base_info_crud.create(info_db_session, item)

        assert created.id is not None
        assert created.category == "department"
        assert created.item_code == "CS"
        assert created.item_name == "计算机科学系"
        assert created.is_active is True

    async def test_get_base_info(self, info_db_session):
        """Get a base info item by primary key."""
        item = _make_item()
        created = await base_info_crud.create(info_db_session, item)

        fetched = await base_info_crud.get(info_db_session, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.item_code == "CS"

    async def test_get_base_info_not_found(self, info_db_session):
        """Get a non-existent item returns None."""
        fetched = await base_info_crud.get(info_db_session, 99999)
        assert fetched is None

    async def test_get_multi_base_infos(self, info_db_session):
        """Get paginated base info list."""
        await base_info_crud.create(info_db_session, _make_item(item_code="CS"))
        await base_info_crud.create(info_db_session, _make_item(item_code="MATH"))

        items = await base_info_crud.get_multi(info_db_session, skip=0, limit=10)
        assert len(items) == 2

    async def test_get_multi_base_infos_pagination(self, info_db_session):
        """Get paginated base info list respects skip/limit."""
        await base_info_crud.create(info_db_session, _make_item(item_code="A"))
        await base_info_crud.create(info_db_session, _make_item(item_code="B"))
        await base_info_crud.create(info_db_session, _make_item(item_code="C"))

        items = await base_info_crud.get_multi(info_db_session, skip=0, limit=2)
        assert len(items) == 2

        items = await base_info_crud.get_multi(info_db_session, skip=2, limit=2)
        assert len(items) == 1

    async def test_update_base_info(self, info_db_session):
        """Update a base info item's fields."""
        item = _make_item()
        created = await base_info_crud.create(info_db_session, item)

        updated = await base_info_crud.update(
            info_db_session,
            created,
            item_name="数学系",
            description="数学与统计系",
        )

        assert updated.item_name == "数学系"
        assert updated.description == "数学与统计系"
        assert updated.item_code == "CS"  # unchanged

    async def test_delete_base_info(self, info_db_session):
        """Delete a base info item and verify it's gone."""
        item = _make_item()
        created = await base_info_crud.create(info_db_session, item)

        deleted = await base_info_crud.delete(info_db_session, created.id)
        assert deleted is True

        fetched = await base_info_crud.get(info_db_session, created.id)
        assert fetched is None

    async def test_delete_base_info_not_found(self, info_db_session):
        """Delete a non-existent item returns False."""
        deleted = await base_info_crud.delete(info_db_session, 99999)
        assert deleted is False

    async def test_get_by_category(self, info_db_session):
        """Get items by category with pagination."""
        await base_info_crud.create(
            info_db_session, _make_item(category="department", item_code="CS")
        )
        await base_info_crud.create(
            info_db_session, _make_item(category="department", item_code="MATH")
        )
        await base_info_crud.create(
            info_db_session, _make_item(category="title", item_code="PROF")
        )

        items, total = await base_info_crud.get_by_category(
            info_db_session, "department", skip=0, limit=10
        )
        assert len(items) == 2
        assert total == 2
        assert all(item.category == "department" for item in items)

    async def test_get_by_category_pagination(self, info_db_session):
        """Get items by category respects pagination."""
        for i in range(5):
            await base_info_crud.create(
                info_db_session, _make_item(category="department", item_code=f"DEPT-{i}")
            )

        items, total = await base_info_crud.get_by_category(
            info_db_session, "department", skip=0, limit=3
        )
        assert len(items) == 3
        assert total == 5

        items, total = await base_info_crud.get_by_category(
            info_db_session, "department", skip=3, limit=3
        )
        assert len(items) == 2
        assert total == 5  # total is independent of skip/limit

    async def test_get_by_category_empty(self, info_db_session):
        """Get items by non-existent category returns empty list."""
        await base_info_crud.create(
            info_db_session, _make_item(category="department", item_code="CS")
        )

        items, total = await base_info_crud.get_by_category(
            info_db_session, "nonexistent", skip=0, limit=10
        )
        assert items == []
        assert total == 0
