"""Unit tests for CourseManagementService — BaseInfo methods."""

import pytest

from info_service.schemas.base_info_schema import (
    BaseInfoCreateRequest,
    BaseInfoPatchRequest,
    BaseInfoUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import ResourceNotFoundError


@pytest.mark.unit
class TestBaseInfoService:
    """Test base info business logic using real in-memory DB."""

    async def test_create_base_info(self, info_db_session):
        """Create a base info item via service."""
        req = BaseInfoCreateRequest(
            category="department",
            item_code="CS",
            item_name="计算机科学系",
            description="计算机科学与技术系",
        )
        item = await course_management_service.create_base_info(info_db_session, req)

        assert item.id is not None
        assert item.category == "department"
        assert item.item_code == "CS"

    async def test_get_base_info(self, info_db_session):
        """Get a base info item by id."""
        req = BaseInfoCreateRequest(
            category="department", item_code="MATH", item_name="数学系"
        )
        created = await course_management_service.create_base_info(info_db_session, req)

        fetched = await course_management_service.get_base_info(info_db_session, created.id)
        assert fetched.id == created.id
        assert fetched.item_code == "MATH"

    async def test_get_base_info_not_found(self, info_db_session):
        """Get non-existent base info raises ResourceNotFoundError."""
        with pytest.raises(ResourceNotFoundError):
            await course_management_service.get_base_info(info_db_session, 99999)

    async def test_list_base_info(self, info_db_session):
        """List base info items."""
        await course_management_service.create_base_info(
            info_db_session, BaseInfoCreateRequest(
                category="department", item_code="CS", item_name="计算机科学系"
            ),
        )
        await course_management_service.create_base_info(
            info_db_session, BaseInfoCreateRequest(
                category="department", item_code="MATH", item_name="数学系"
            ),
        )

        items, total = await course_management_service.list_base_info(info_db_session)
        assert len(items) == 2

    async def test_list_base_info_by_category(self, info_db_session):
        """List base info filtered by category."""
        await course_management_service.create_base_info(
            info_db_session, BaseInfoCreateRequest(
                category="department", item_code="CS", item_name="计算机科学系"
            ),
        )
        await course_management_service.create_base_info(
            info_db_session, BaseInfoCreateRequest(
                category="title", item_code="PROF", item_name="教授"
            ),
        )

        items, total = await course_management_service.list_base_info(
            info_db_session, category="department"
        )
        assert len(items) == 1
        assert total == 1
        assert items[0].category == "department"

    async def test_list_base_info_empty_category(self, info_db_session):
        """List base info with non-matching category returns empty."""
        await course_management_service.create_base_info(
            info_db_session, BaseInfoCreateRequest(
                category="department", item_code="CS", item_name="计算机科学系"
            ),
        )

        items, total = await course_management_service.list_base_info(
            info_db_session, category="nonexistent"
        )
        assert items == []
        assert total == 0

    async def test_update_base_info(self, info_db_session):
        """Full update a base info item."""
        req = BaseInfoCreateRequest(
            category="department", item_code="CS", item_name="原始名称"
        )
        created = await course_management_service.create_base_info(info_db_session, req)

        update_req = BaseInfoUpdateRequest(
            category="department",
            item_code="CS_UPDATED",
            item_name="更新后名称",
            description="新描述",
            is_active=False,
        )
        updated = await course_management_service.update_base_info(
            info_db_session, created.id, update_req
        )

        assert updated.item_code == "CS_UPDATED"
        assert updated.item_name == "更新后名称"
        assert updated.is_active is False

    async def test_patch_base_info(self, info_db_session):
        """Partial update only changes provided fields."""
        req = BaseInfoCreateRequest(
            category="department", item_code="CS", item_name="原始名称"
        )
        created = await course_management_service.create_base_info(info_db_session, req)

        patch_req = BaseInfoPatchRequest(item_name="补丁更新名称")
        patched = await course_management_service.patch_base_info(
            info_db_session, created.id, patch_req
        )

        assert patched.item_name == "补丁更新名称"
        assert patched.item_code == "CS"  # unchanged
        assert patched.category == "department"  # unchanged

    async def test_delete_base_info(self, info_db_session):
        """Delete a base info item."""
        req = BaseInfoCreateRequest(
            category="department", item_code="CS", item_name="计算机科学系"
        )
        created = await course_management_service.create_base_info(info_db_session, req)

        await course_management_service.delete_base_info(info_db_session, created.id)

        with pytest.raises(ResourceNotFoundError):
            await course_management_service.get_base_info(info_db_session, created.id)
