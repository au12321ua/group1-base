"""Tests for SessionCRUD."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import select

from auth_service.crud.session_crud import session_crud
from auth_service.crud.token_crud import token_crud
from auth_service.models.session import AuthenticationSession, SessionStatus
from auth_service.models.token import TokenType


def _expires_in_hours(hours: int) -> datetime:
    return datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=hours)


@pytest.mark.unit
class TestSessionCRUD:
    """测试登录会话生命周期。"""

    async def test_create_end_and_expire_session(self, auth_db_session) -> None:
        """应能创建会话并标记为 ENDED 或 EXPIRED。"""
        access = await token_crud.create(
            auth_db_session,
            user_id="sess-u1",
            token_type=TokenType.ACCESS,
            token_value="access-s1",
            expires_at=_expires_in_hours(1),
        )
        refresh = await token_crud.create(
            auth_db_session,
            user_id="sess-u1",
            token_type=TokenType.REFRESH,
            token_value="refresh-s1",
            expires_at=_expires_in_hours(24),
        )
        session = await session_crud.create(
            auth_db_session,
            user_id="sess-u1",
            access_token_id=access.id,
            refresh_token_id=refresh.id,
            client_ip="127.0.0.1",
        )
        assert session.status == SessionStatus.ACTIVE

        await session_crud.end_session(auth_db_session, session.id)
        await auth_db_session.refresh(session)
        assert session.status == SessionStatus.ENDED
        assert session.ended_at is not None

        session2 = await session_crud.create(
            auth_db_session,
            user_id="sess-u1",
            access_token_id=access.id,
            refresh_token_id=refresh.id,
        )
        await session_crud.expire_session(auth_db_session, session2.id)
        await auth_db_session.refresh(session2)
        assert session2.status == SessionStatus.EXPIRED

    async def test_delete_by_user(self, auth_db_session) -> None:
        """应能删除用户全部会话记录。"""
        access = await token_crud.create(
            auth_db_session,
            user_id="sess-u2",
            token_type=TokenType.ACCESS,
            token_value="access-s2",
            expires_at=_expires_in_hours(1),
        )
        refresh = await token_crud.create(
            auth_db_session,
            user_id="sess-u2",
            token_type=TokenType.REFRESH,
            token_value="refresh-s2",
            expires_at=_expires_in_hours(24),
        )
        await session_crud.create(
            auth_db_session,
            user_id="sess-u2",
            access_token_id=access.id,
            refresh_token_id=refresh.id,
        )
        await session_crud.delete_by_user(auth_db_session, "sess-u2")
        result = await auth_db_session.exec(
            select(AuthenticationSession).where(AuthenticationSession.user_id == "sess-u2")
        )
        assert result.first() is None
