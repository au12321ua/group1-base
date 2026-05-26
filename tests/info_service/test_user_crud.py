"""Unit tests for UserInfo CRUD and UserProfile CRUD."""

import pytest

from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile


@pytest.mark.unit
class TestUserInfoCRUD:
    """UserInfo CRUD operations."""

    async def test_get_by_id(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        fetched = await user_crud.get_by_id(info_db_session, user.id)
        assert fetched is not None
        assert fetched.user_no == "S001"

    async def test_get_by_id_not_found(self, info_db_session):
        fetched = await user_crud.get_by_id(info_db_session, 99999)
        assert fetched is None

    async def test_get_by_user_no(self, info_db_session):
        await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        fetched = await user_crud.get_by_user_no(info_db_session, "S001")
        assert fetched is not None
        assert fetched.username == "alice"

    async def test_get_by_username(self, info_db_session):
        await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        fetched = await user_crud.get_by_username(info_db_session, "alice")
        assert fetched is not None
        assert fetched.user_no == "S001"

    async def test_create_user(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S002", username="bob", role_ids="1,2")
        )
        assert user.id is not None
        assert user.user_no == "S002"
        assert user.is_deleted is False

    async def test_update_user(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S003", username="charlie")
        )
        updated = await user_crud.update(
            info_db_session, user, user_no="S003-NEW", role_ids="3"
        )
        assert updated.user_no == "S003-NEW"
        assert updated.role_ids == "3"

    async def test_get_multi_pagination(self, info_db_session):
        for i in range(3):
            await user_crud.create(
                info_db_session, UserInfo(user_no=f"S00{i}", username=f"user{i}")
            )
        items, total = await user_crud.get_multi(info_db_session, skip=0, limit=2)
        assert len(items) == 2
        assert total == 3

    async def test_get_multi_keyword(self, info_db_session):
        await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        # Create profile for keyword search by full_name
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S002", username="bob")
        )
        await user_profile_crud.create(
            info_db_session,
            UserProfile(user_id=user.id, full_name="张三"),
        )
        items, total = await user_crud.get_multi(
            info_db_session, keyword="alice", skip=0, limit=10
        )
        assert len(items) == 1
        assert items[0].username == "alice"

    async def test_get_multi_include_deleted(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        await user_crud.logical_delete(info_db_session, user.id)

        items, total = await user_crud.get_multi(info_db_session)
        assert len(items) == 0  # default excludes deleted

        items, total = await user_crud.get_multi(
            info_db_session, include_deleted=True
        )
        assert len(items) == 1
        assert items[0].is_deleted is True

    async def test_logical_delete(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        await user_crud.logical_delete(info_db_session, user.id)

        fetched = await user_crud.get_by_id(info_db_session, user.id)
        assert fetched.is_deleted is True
        assert fetched.deleted_at is not None

    async def test_restore(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        await user_crud.logical_delete(info_db_session, user.id)
        await user_crud.restore(info_db_session, user.id)

        fetched = await user_crud.get_by_id(info_db_session, user.id)
        assert fetched.is_deleted is False
        assert fetched.deleted_at is None

    async def test_physical_delete(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="alice")
        )
        await user_crud.physical_delete(info_db_session, user.id)

        fetched = await user_crud.get_by_id(info_db_session, user.id)
        assert fetched is None


@pytest.mark.unit
class TestUserProfileCRUD:
    """UserProfile CRUD operations."""

    async def test_create_profile(self, info_db_session):
        profile = await user_profile_crud.create(
            info_db_session,
            UserProfile(user_id=1, full_name="测试用户", email="test@test.com"),
        )
        assert profile.id is not None
        assert profile.full_name == "测试用户"

    async def test_get_by_user_id(self, info_db_session):
        await user_profile_crud.create(
            info_db_session,
            UserProfile(user_id=1, full_name="测试用户"),
        )
        fetched = await user_profile_crud.get_by_user_id(info_db_session, 1)
        assert fetched is not None
        assert fetched.full_name == "测试用户"

    async def test_get_by_user_id_not_found(self, info_db_session):
        fetched = await user_profile_crud.get_by_user_id(info_db_session, 99999)
        assert fetched is None

    async def test_update_profile(self, info_db_session):
        profile = await user_profile_crud.create(
            info_db_session,
            UserProfile(user_id=1, full_name="原始名称"),
        )
        updated = await user_profile_crud.update(
            info_db_session, profile, full_name="新名称", phone="13900000000"
        )
        assert updated.full_name == "新名称"
        assert updated.phone == "13900000000"

    async def test_delete_profile(self, info_db_session):
        await user_profile_crud.create(
            info_db_session,
            UserProfile(user_id=1, full_name="测试用户"),
        )
        await user_profile_crud.delete(info_db_session, 1)

        fetched = await user_profile_crud.get_by_user_id(info_db_session, 1)
        assert fetched is None
