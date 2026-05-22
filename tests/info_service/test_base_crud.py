"""Unit tests for shared BaseCRUD helpers."""

import pytest

from info_service.crud.base import BaseCRUD
from info_service.models.base_info_item import BaseInfoItem


@pytest.mark.unit
class TestBaseCrud:
    """Verify generic BaseCRUD behavior."""

    async def test_get_multi_returns_rows_in_primary_key_order(self, info_db_session):
        """Generic pagination should apply a deterministic primary-key sort."""
        crud = BaseCRUD(BaseInfoItem)

        third = await crud.create(
            info_db_session,
            BaseInfoItem(category="department", item_code="C", item_name="Third"),
        )
        first = await crud.create(
            info_db_session,
            BaseInfoItem(category="department", item_code="A", item_name="First"),
        )
        second = await crud.create(
            info_db_session,
            BaseInfoItem(category="department", item_code="B", item_name="Second"),
        )
        await info_db_session.commit()

        items = await crud.get_multi(info_db_session, skip=1, limit=2)

        assert [item.id for item in items] == [first.id, second.id]
        assert third.id is not None
