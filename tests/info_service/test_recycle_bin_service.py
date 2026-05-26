"""Unit tests for RecycleBinService."""

import pytest

from info_service.crud.user_crud import user_crud
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.models.user import UserInfo
from info_service.models.user_profile import UserProfile
from info_service.services.recycle_bin_service import recycle_bin_service
from shared.exceptions import BusinessRuleError, ResourceNotFoundError


async def _setup_deleted_user(db, user_no="S001", username="deleted_user"):
    """Helper: create and soft-delete a user."""
    user = await user_crud.create(
        db, UserInfo(user_no=user_no, username=username, role_ids="1")
    )
    await user_profile_crud.create(
        db, UserProfile(user_id=user.id, full_name="已删除用户")
    )
    await user_crud.logical_delete(db, user.id)
    return user


@pytest.mark.unit
class TestRecycleBinService:
    """RecycleBinService unit tests — Info DB operations."""

    async def test_list_deleted_users(self, info_db_session):
        await _setup_deleted_user(info_db_session, user_no="S001", username="alice")
        await _setup_deleted_user(info_db_session, user_no="S002", username="bob")
        # Create a non-deleted user
        await user_crud.create(
            info_db_session, UserInfo(user_no="S003", username="charlie")
        )

        items, total = await recycle_bin_service.list_deleted_users(info_db_session)
        # Only deleted users should be returned
        assert len(items) == 2
        assert all(u.is_deleted for u in items)

    async def test_restore_user(self, info_db_session):
        user = await _setup_deleted_user(info_db_session)

        await recycle_bin_service.restore_user(info_db_session, user.id)

        fetched = await user_crud.get_by_id(info_db_session, user.id)
        assert fetched.is_deleted is False
        assert fetched.deleted_at is None

    async def test_restore_user_not_found(self, info_db_session):
        with pytest.raises(ResourceNotFoundError):
            await recycle_bin_service.restore_user(info_db_session, 99999)

    async def test_restore_user_not_deleted(self, info_db_session):
        user = await user_crud.create(
            info_db_session, UserInfo(user_no="S001", username="active_user")
        )
        with pytest.raises(BusinessRuleError):
            await recycle_bin_service.restore_user(info_db_session, user.id)

    async def test_physical_delete_user(self, info_db_session):
        user = await _setup_deleted_user(info_db_session)

        await recycle_bin_service.physical_delete_user(info_db_session, user.id)

        fetched = await user_crud.get_by_id(info_db_session, user.id)
        assert fetched is None
        profile = await user_profile_crud.get_by_user_id(info_db_session, user.id)
        assert profile is None

    async def test_batch_physical_delete(self, info_db_session):
        user1 = await _setup_deleted_user(info_db_session, user_no="S001", username="alice")
        user2 = await _setup_deleted_user(info_db_session, user_no="S002", username="bob")

        await recycle_bin_service.batch_physical_delete(
            info_db_session, [user1.id, user2.id]
        )

        assert await user_crud.get_by_id(info_db_session, user1.id) is None
        assert await user_crud.get_by_id(info_db_session, user2.id) is None
