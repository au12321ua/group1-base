"""Tests for TokenCRUD."""

from datetime import UTC, datetime, timedelta

import pytest

from auth_service.crud.token_crud import token_crud
from auth_service.models.token import TokenType


@pytest.mark.unit
class TestTokenCRUD:
    """测试 Token 持久化、查询与吊销。"""

    async def test_create_get_and_revoke(self, auth_db_session) -> None:
        """应能创建、按值查询并吊销 Token。"""
        expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)
        token = await token_crud.create(
            auth_db_session,
            user_id="tok-u1",
            token_type=TokenType.REFRESH,
            token_value="refresh-jwt-value",
            expires_at=expires,
        )

        found = await token_crud.get_by_value(auth_db_session, "refresh-jwt-value")
        assert found is not None
        assert found.id == token.id

        await token_crud.revoke(auth_db_session, token.id)
        revoked = await token_crud.get_by_value(auth_db_session, "refresh-jwt-value")
        assert revoked is not None
        assert revoked.revoked_at is not None

    async def test_revoke_all_for_user(self, auth_db_session) -> None:
        """应能吊销某用户全部未撤销 Token。"""
        expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)
        t1 = await token_crud.create(
            auth_db_session,
            user_id="tok-u2",
            token_type=TokenType.ACCESS,
            token_value="access-1",
            expires_at=expires,
        )
        t2 = await token_crud.create(
            auth_db_session,
            user_id="tok-u2",
            token_type=TokenType.REFRESH,
            token_value="refresh-2",
            expires_at=expires,
        )

        await token_crud.revoke_all_for_user(auth_db_session, "tok-u2")
        assert (await token_crud.get_by_value(auth_db_session, t1.token_value)).revoked_at
        assert (await token_crud.get_by_value(auth_db_session, t2.token_value)).revoked_at

    async def test_delete_by_user(self, auth_db_session) -> None:
        """应能删除用户全部 Token 记录。"""
        expires = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)
        await token_crud.create(
            auth_db_session,
            user_id="tok-u3",
            token_type=TokenType.ACCESS,
            token_value="access-del",
            expires_at=expires,
        )
        await token_crud.delete_by_user(auth_db_session, "tok-u3")
        assert await token_crud.get_by_value(auth_db_session, "access-del") is None
