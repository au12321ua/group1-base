"""Tests for IdentityService."""

import pytest

from auth_service.core.security import create_access_token, create_service_token
from auth_service.models.permission import Permission, RolePermission
from auth_service.models.role import Role
from auth_service.schemas.auth_schema import InternalVerifyRequest
from auth_service.services.identity_service import identity_service


@pytest.fixture
async def service_role_with_permissions(auth_db_session) -> dict:
    """创建 SERVICE 角色并分配测试权限，返回角色信息。"""
    role = Role(code="SERVICE", name="系统服务")
    auth_db_session.add(role)
    await auth_db_session.flush()

    perm = Permission(
        code="data-provision:read",
        name="查看数据供给",
        resource="data-provision",
        action="read",
    )
    auth_db_session.add(perm)
    await auth_db_session.flush()

    auth_db_session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    await auth_db_session.commit()

    return {"role_id": role.id, "permission_code": "data-provision:read"}


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

    async def test_verify_service_token_resolves_permissions_from_db(
        self,
        auth_db_session,
        auth_security_env,
        service_role_with_permissions,
    ) -> None:
        """Service Token 应从 DB 的 SERVICE 角色获取权限，而非 JWT scope。"""
        token = create_service_token(
            client_id="course_arrangement",
            audience="info_service",
        )
        response = await identity_service.verify_token(
            auth_db_session,
            InternalVerifyRequest(token=token),
        )

        assert response.token_type == "service"
        assert response.role == "SERVICE"
        assert response.user_id == "course_arrangement"
        # Permissions come from DB SERVICE role, not token payload
        assert "data-provision:read" in response.permissions
