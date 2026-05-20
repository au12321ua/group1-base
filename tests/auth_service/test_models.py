"""Tests for auth_service models."""

from datetime import datetime

import pytest
from sqlmodel import select

from auth_service.models.credential import Credential
from auth_service.models.permission import Permission, RolePermission
from auth_service.models.role import Role
from auth_service.models.user import User, UserStatus


@pytest.mark.unit
class TestAuthModels:
    """测试 Auth 领域模型的基础持久化与默认值。"""

    async def test_user_default_status_is_active(self, auth_db_session):
        """创建 User 时，status 默认值应为 ACTIVE。"""
        user = User(user_id="u-model-001", username="model-user")
        auth_db_session.add(user)
        await auth_db_session.flush()

        assert user.id is not None
        assert user.status == UserStatus.ACTIVE

    async def test_credential_default_fields(self, auth_db_session):
        """Credential 默认字段应自动填充并可持久化。"""
        credential = Credential(
            user_id="u-model-002",
            username="alice",
            password_hash="hashed-password",
            password_salt="salt",
        )
        auth_db_session.add(credential)
        await auth_db_session.flush()

        assert credential.id is not None
        assert credential.failed_login_count == 0
        assert credential.locked_until is None
        assert isinstance(credential.created_at, datetime)
        assert isinstance(credential.updated_at, datetime)

    async def test_permission_and_role_permission_persistence(self, auth_db_session):
        """Permission 与 RolePermission 关联记录应可创建并查询。"""
        role = Role(code="SYS_ADMIN", name="System Admin")
        permission = Permission(
            code="user:read",
            name="Read User",
            resource="user",
            action="read",
        )

        auth_db_session.add(role)
        auth_db_session.add(permission)
        await auth_db_session.flush()

        assert role.id is not None
        assert permission.id is not None

        role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
        auth_db_session.add(role_permission)
        await auth_db_session.flush()

        stmt = select(RolePermission).where(RolePermission.role_id == role.id)
        result = await auth_db_session.exec(stmt)
        found = result.first()

        assert found is not None
        assert found.permission_id == permission.id
