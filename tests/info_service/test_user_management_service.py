"""Unit tests for UserManagementService — Info DB operations.

Note: create_user and Auth-syncing methods require a running Auth Service
and are tested in integration tests (QA responsibility).
These unit tests cover Info DB operations that don't require Auth.
"""

import pytest

from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.schemas.user_schema import (
    UserPatchRequest,
    UserUpdateRequest,
)
from info_service.services.user_management_service import user_management_service
from shared.exceptions import ResourceNotFoundError


async def _setup_user(db, user_no="S001", username="alice", full_name="测试用户"):
    """Helper: create a user + profile for testing."""
    user = await user_crud.create(
        db, UserInfo(user_no=user_no, username=username, role_ids="1")
    )
    await user_profile_crud.create(
        db,
        UserProfile(
            user_id=user.id,
            full_name=full_name,
            email=f"{username}@test.com",
            status="ACTIVE",
        ),
    )
    user.profile_id = user.id  # approximate
    await db.flush()
    return user


@pytest.mark.unit
class TestUserManagementService:
    """User management service unit tests (Info DB only, Auth not required)."""

    async def test_get_user(self, info_db_session):
        user = await _setup_user(info_db_session)
        result = await user_management_service.get_user(info_db_session, user.id)
        assert result.user_no == "S001"
        assert result.username == "alice"
        assert result.profile is not None
        assert result.profile.full_name == "测试用户"

    async def test_get_user_not_found(self, info_db_session):
        with pytest.raises(ResourceNotFoundError):
            await user_management_service.get_user(info_db_session, 99999)

    async def test_list_users(self, info_db_session):
        await _setup_user(info_db_session, user_no="S001", username="alice")
        await _setup_user(info_db_session, user_no="S002", username="bob")

        items, total = await user_management_service.list_users(info_db_session)
        assert len(items) == 2
        assert total == 2

    async def test_list_users_keyword(self, info_db_session):
        await _setup_user(info_db_session, user_no="S001", username="alice")
        await _setup_user(info_db_session, user_no="S002", username="bob")

        items, total = await user_management_service.list_users(
            info_db_session, keyword="alice"
        )
        assert len(items) == 1
        assert items[0].username == "alice"

    async def test_update_user(self, info_db_session):
        user = await _setup_user(info_db_session)
        req = UserUpdateRequest(
            user_no="S001-NEW",
            username="alice_new",
            role_ids=[1, 2],
            full_name="新名称",
            gender="FEMALE",
            email="new@test.com",
            phone="13800000000",
            status="ACTIVE",
        )
        result = await user_management_service.update_user(
            info_db_session, user.id, req
        )
        assert result.user_no == "S001-NEW"
        assert result.username == "alice_new"
        assert result.role_ids == "1,2"
        assert result.profile.full_name == "新名称"

    async def test_patch_user(self, info_db_session):
        user = await _setup_user(info_db_session)
        req = UserPatchRequest(full_name="补丁名称", phone="13911111111")
        result = await user_management_service.patch_user(
            info_db_session, user.id, req
        )
        assert result.profile.full_name == "补丁名称"
        assert result.profile.phone == "13911111111"
        assert result.user_no == "S001"  # unchanged

    async def test_disable_user(self, info_db_session):
        user = await _setup_user(info_db_session)
        await user_management_service.disable_user(info_db_session, user.id)

        profile = await user_profile_crud.get_by_user_id(info_db_session, user.id)
        assert profile.status == "DISABLED"

    async def test_enable_user(self, info_db_session):
        user = await _setup_user(info_db_session)
        await user_management_service.disable_user(info_db_session, user.id)
        await user_management_service.enable_user(info_db_session, user.id)

        profile = await user_profile_crud.get_by_user_id(info_db_session, user.id)
        assert profile.status == "ACTIVE"
