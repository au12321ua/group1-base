"""Tests for CredentialCRUD."""

from datetime import UTC, datetime, timedelta

import pytest

from auth_service.core.security import get_password_hash
from auth_service.core.time_utils import as_utc
from auth_service.crud.credential_crud import credential_crud


@pytest.mark.unit
class TestCredentialCRUD:
    """测试凭据 CRUD 与登录保护相关字段更新。"""

    async def test_create_and_get_by_user_id_and_username(self, auth_db_session) -> None:
        """创建凭据后应能按 user_id 与 username 查询。"""
        password_hash, password_salt = get_password_hash("login-pass")
        created = await credential_crud.create(
            auth_db_session,
            user_id="cred-u1",
            username="alice",
            password_hash=password_hash,
            password_salt=password_salt,
        )

        by_user = await credential_crud.get_by_user_id(auth_db_session, "cred-u1")
        by_name = await credential_crud.get_by_username(auth_db_session, "alice")

        assert created.id is not None
        assert by_user is not None
        assert by_name is not None
        assert by_user.user_id == by_name.user_id == "cred-u1"

    async def test_increment_and_reset_failed_count(self, auth_db_session) -> None:
        """失败计数递增后应可重置为 0。"""
        password_hash, password_salt = get_password_hash("x")
        await credential_crud.create(
            auth_db_session,
            user_id="cred-u2",
            username="bob",
            password_hash=password_hash,
            password_salt=password_salt,
        )

        count = await credential_crud.increment_failed_count(auth_db_session, "cred-u2")
        assert count == 1
        count = await credential_crud.increment_failed_count(auth_db_session, "cred-u2")
        assert count == 2

        await credential_crud.reset_failed_count(auth_db_session, "cred-u2")
        cred = await credential_crud.get_by_user_id(auth_db_session, "cred-u2")
        assert cred is not None
        assert cred.failed_login_count == 0

    async def test_lock_and_unlock_account(self, auth_db_session) -> None:
        """应能设置与清除 locked_until。"""
        password_hash, password_salt = get_password_hash("x")
        await credential_crud.create(
            auth_db_session,
            user_id="cred-u3",
            username="carol",
            password_hash=password_hash,
            password_salt=password_salt,
        )
        until = datetime.now(UTC) + timedelta(minutes=10)
        await credential_crud.lock_account(auth_db_session, "cred-u3", until)

        cred = await credential_crud.get_by_user_id(auth_db_session, "cred-u3")
        assert cred is not None
        assert cred.locked_until is not None
        assert as_utc(cred.locked_until) == until

        await credential_crud.unlock_account(auth_db_session, "cred-u3")
        cred = await credential_crud.get_by_user_id(auth_db_session, "cred-u3")
        assert cred is not None
        assert cred.locked_until is None

    async def test_update_password_and_delete(self, auth_db_session) -> None:
        """应能更新密码哈希并删除记录。"""
        h1, s1 = get_password_hash("old")
        await credential_crud.create(
            auth_db_session,
            user_id="cred-u4",
            username="dave",
            password_hash=h1,
            password_salt=s1,
        )
        h2, s2 = get_password_hash("new")
        updated = await credential_crud.update_password(auth_db_session, "cred-u4", h2, s2)
        assert updated is not None
        assert updated.password_hash == h2

        deleted = await credential_crud.delete(auth_db_session, "cred-u4")
        assert deleted is True
        assert await credential_crud.get_by_user_id(auth_db_session, "cred-u4") is None
