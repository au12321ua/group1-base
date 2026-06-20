"""Unit tests for UserManagementService — Info DB operations."""

from unittest.mock import AsyncMock

import pytest

from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.schemas.user_schema import (
    UserCreateRequest,
    UserPatchRequest,
    UserUpdateRequest,
)
from info_service.services.user_management_service import user_management_service
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


async def _setup_user(db, user_no="S001", username="alice", full_name="测试用户"):
    """Helper: create a user + profile for testing."""
    user = await user_crud.create(
        db, UserInfo(user_no=user_no, username=username)
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
    await db.flush()
    return user


async def _setup_user_without_profile(db, user_no="S010", username="solo"):
    """Helper: create only the UserInfo row."""
    user = await user_crud.create(
        db,
        UserInfo(user_no=user_no, username=username),
    )
    await db.flush()
    return user


@pytest.mark.unit
class TestUserManagementService:
    """User management service unit tests (Info DB only)."""

    @pytest.fixture(autouse=True)
    def mock_role_name_fetch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Avoid external Auth HTTP calls when assembling user responses."""
        monkeypatch.setattr(
            "info_service.services.user_management_service.batch_fetch_role_names",
            AsyncMock(return_value={}),
        )
        monkeypatch.setattr(
            user_management_service,
            "_sync_roles_to_auth",
            AsyncMock(return_value=True),
        )

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
        assert result.role_ids == ""
        assert result.profile.full_name == "新名称"

    async def test_patch_user(self, info_db_session):
        user = await _setup_user(info_db_session)
        req = UserPatchRequest(full_name="补丁名称", phone="13911111111")
        result = await user_management_service.patch_user(
            info_db_session, user.id, req
        )
        assert result.profile.full_name == "补丁名称"
        assert result.profile.phone == "13911111111"
        assert result.user_no == "S001"

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

    async def test_create_user(self, info_db_session, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            user_management_service,
            "_sync_create_to_auth",
            AsyncMock(return_value=True),
        )

        result = await user_management_service.create_user(
            info_db_session,
            UserCreateRequest(
                user_no="S100",
                username="created_user",
                role_ids=[1, 2],
                full_name="新建用户",
                gender="MALE",
                email="created_user@test.com",
                phone="13811110000",
            ),
        )

        stored_user = await user_crud.get_by_username(info_db_session, "created_user")
        stored_profile = await user_profile_crud.get_by_user_id(info_db_session, stored_user.id)

        assert result.username == "created_user"
        assert stored_user is not None
        assert stored_profile is not None
        assert stored_profile.full_name == "新建用户"

    async def test_create_user_rolls_back_when_auth_create_fails(
        self, info_db_session, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(
            user_management_service,
            "_sync_create_to_auth",
            AsyncMock(return_value=False),
        )

        with pytest.raises(BusinessRuleError, match="Failed to create user in Auth Service"):
            await user_management_service.create_user(
                info_db_session,
                UserCreateRequest(
                    user_no="S101",
                    username="rollback_user",
                    role_ids=[],
                    full_name="回滚用户",
                    gender="FEMALE",
                    email="rollback_user@test.com",
                    phone="13811110001",
                ),
            )

        assert await user_crud.get_by_username(info_db_session, "rollback_user") is None

    async def test_update_user_creates_missing_profile(self, info_db_session):
        user = await _setup_user_without_profile(
            info_db_session,
            user_no="S102",
            username="profile_from_update",
        )

        result = await user_management_service.update_user(
            info_db_session,
            user.id,
            UserUpdateRequest(
                user_no="S102-U",
                username="profile_from_update_u",
                role_ids=[],
                full_name="补建档案",
                gender="MALE",
                email="profile_from_update_u@test.com",
                phone="13811110002",
                status="ACTIVE",
            ),
        )

        assert result.username == "profile_from_update_u"
        assert result.profile is not None
        assert result.profile.full_name == "补建档案"

    async def test_patch_user_creates_missing_profile_and_syncs_role_ids(self, info_db_session):
        user = await _setup_user_without_profile(
            info_db_session,
            user_no="S103",
            username="profile_from_patch",
        )

        result = await user_management_service.patch_user(
            info_db_session,
            user.id,
            UserPatchRequest(
                full_name="补丁创建档案",
                phone="13811110003",
                role_ids=[9],
            ),
        )

        assert result.user_no == "S103"
        assert result.profile is not None
        assert result.profile.full_name == "补丁创建档案"
        assert result.profile.phone == "13811110003"

    async def test_logical_delete_user_rolls_back_when_sync_disable_fails(
        self, info_db_session, monkeypatch: pytest.MonkeyPatch
    ):
        user = await _setup_user(
            info_db_session,
            user_no="S104",
            username="delete_rollback",
        )
        monkeypatch.setattr(
            user_management_service,
            "_sync_disable_to_auth",
            AsyncMock(side_effect=RuntimeError("disable failed")),
        )

        with pytest.raises(BusinessRuleError, match="Failed to disable user in Auth Service"):
            await user_management_service.logical_delete_user(info_db_session, user.id)

        stored_user = await user_crud.get_by_id(info_db_session, user.id)
        assert stored_user.is_deleted is False

    async def test_batch_import_users_reports_partial_success(
        self, info_db_session, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(
            user_management_service,
            "_sync_create_to_auth",
            AsyncMock(return_value=True),
        )
        await _setup_user(
            info_db_session,
            user_no="S105",
            username="existing_user",
        )

        csv_content = (
            "user_no,username,full_name,gender,email,phone\n"
            "S106,batch_user_1,批量用户1,MALE,batch1@test.com,13811110004\n"
            "S105,duplicate_no,重复学号,MALE,dup@test.com,13811110005\n"
            "S107,,缺少用户名,FEMALE,missing@test.com,13811110006\n"
        ).encode()

        result = await user_management_service.batch_import_users(info_db_session, csv_content)

        assert result.total == 3
        assert result.success_count == 1
        assert result.failed_count == 2
        assert len(result.errors) == 2
        assert await user_crud.get_by_username(info_db_session, "batch_user_1") is not None

    async def test_batch_import_users_captures_row_exception(
        self, info_db_session, monkeypatch: pytest.MonkeyPatch
    ):
        async def fake_create_user(db, request, current_user=None):
            if request.username == "bad_user":
                raise RuntimeError("boom")
            return object()

        monkeypatch.setattr(user_management_service, "create_user", fake_create_user)

        csv_content = (
            "user_no,username,full_name,gender,email,phone\n"
            "S108,good_user,正常用户,MALE,good@test.com,13811110007\n"
            "S109,bad_user,异常用户,MALE,bad@test.com,13811110008\n"
        ).encode()

        result = await user_management_service.batch_import_users(info_db_session, csv_content)

        assert result.total == 2
        assert result.success_count == 1
        assert result.failed_count == 1
        assert result.errors == [{"row": "3", "error": "boom"}]
