"""Tests for IdentityService."""

import pytest

from auth_service.core.security import create_access_token, create_service_token
from auth_service.schemas.auth_schema import InternalVerifyRequest
from auth_service.services.identity_service import identity_service


@pytest.mark.unit
class TestIdentityService:
    """测试 Gateway 调用的 Token 验签与身份提取。"""

    async def test_verify_access_token_returns_user_identity(
        self, auth_db_session, seeded_auth_user, auth_security_env
    ) -> None:
        """Access Token 应解析出用户 ID、角色与权限列表。"""
        token = create_access_token(
            seeded_auth_user["user_id"],
            "STUDENT",
            permissions=["course:read"],
        )
        response = await identity_service.verify_token(
            auth_db_session,
            InternalVerifyRequest(token=token),
        )

        assert response.user_id == "seed-u1"
        assert response.username == "seeduser"
        assert response.role == "STUDENT"
        assert "course:read" in response.permissions
        assert response.token_type == "access"

    async def test_verify_service_token_returns_scope_permissions(
        self, auth_db_session, auth_security_env
    ) -> None:
        """Service Token 应将 scope 拆分为权限列表。"""
        token = create_service_token(
            client_id="course_arrangement",
            scope="teacher:read,calendar:read",
            audience="info_service",
        )
        response = await identity_service.verify_token(
            auth_db_session,
            InternalVerifyRequest(token=token),
        )

        assert response.token_type == "service"
        assert response.role == "SERVICE"
        assert "teacher:read" in response.permissions
        assert "calendar:read" in response.permissions

    async def test_verify_service_token_parses_space_separated_scope(
        self, auth_db_session, auth_security_env
    ) -> None:
        """Service Token scope 应支持配置默认的空格分隔格式。"""
        token = create_service_token(
            client_id="info_service",
            scope="user:read course:read calendar:read",
            audience="info_service",
        )
        response = await identity_service.verify_token(
            auth_db_session,
            InternalVerifyRequest(token=token),
        )

        assert response.permissions == ["user:read", "course:read", "calendar:read"]
