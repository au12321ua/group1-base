"""Tests for AuthService business logic."""

import pytest

from auth_service.core.security import verify_token
from auth_service.schemas.auth_schema import ChangePasswordRequest
from auth_service.services.auth_service import auth_service
from shared.exceptions import (
    AccountLockedError,
    AuthenticationError,
    BusinessRuleError,
    ServiceCredentialInvalidError,
)


@pytest.mark.unit
class TestAuthServiceLogin:
    """测试登录、登出与 Token 刷新。"""

    async def test_login_success(
        self, auth_db_session, seeded_auth_user, auth_security_env
    ) -> None:
        """正确密码应返回 token 对。"""
        result = await auth_service.login(
            auth_db_session,
            seeded_auth_user["username"],
            seeded_auth_user["password"],
        )

        assert result.access_token
        assert result.refresh_token
        assert result.user_id == "seed-u1"
        assert result.role == "STUDENT"
        payload = verify_token(result.access_token)
        assert payload["type"] == "access"

    async def test_login_wrong_password(
        self, auth_db_session, seeded_auth_user, auth_security_env
    ) -> None:
        """错误密码应抛出 AuthenticationError。"""
        with pytest.raises(AuthenticationError):
            await auth_service.login(auth_db_session, seeded_auth_user["username"], "wrong")

    async def test_login_locks_after_max_failures(
        self, auth_db_session, seeded_auth_user, auth_security_env, monkeypatch
    ) -> None:
        """连续失败达到上限应锁定账户。"""
        from auth_service.core.config import get_auth_settings

        monkeypatch.setenv("MAX_LOGIN_ATTEMPTS", "2")
        get_auth_settings.cache_clear()

        with pytest.raises(AuthenticationError):
            await auth_service.login(auth_db_session, seeded_auth_user["username"], "bad1")
        with pytest.raises(AuthenticationError):
            await auth_service.login(auth_db_session, seeded_auth_user["username"], "bad2")
        with pytest.raises(AccountLockedError):
            await auth_service.login(auth_db_session, seeded_auth_user["username"], "bad3")

        get_auth_settings.cache_clear()

    async def test_logout_and_refresh_flow(
        self, auth_db_session, seeded_auth_user, auth_security_env
    ) -> None:
        """登出后 refresh 应失败；未登出时 refresh 应轮换 token。"""
        login = await auth_service.login(
            auth_db_session,
            seeded_auth_user["username"],
            seeded_auth_user["password"],
        )
        refreshed = await auth_service.refresh_token(auth_db_session, login.refresh_token)
        assert refreshed.access_token != login.access_token

        login2 = await auth_service.login(
            auth_db_session,
            seeded_auth_user["username"],
            seeded_auth_user["password"],
        )
        await auth_service.logout(auth_db_session, login2.refresh_token)
        from shared.exceptions import TokenExpiredError

        with pytest.raises((AuthenticationError, TokenExpiredError)):
            await auth_service.refresh_token(auth_db_session, login2.refresh_token)


@pytest.mark.unit
class TestAuthServiceInternal:
    """测试 Info Service 调用的内部用户生命周期。"""

    async def test_create_disable_enable_delete_user(
        self, auth_db_session, auth_security_env
    ) -> None:
        """应能创建、禁用、启用并物理删除用户。"""
        from auth_service.models.role import Role

        role = Role(code="TEACHER", name="Teacher")
        auth_db_session.add(role)
        await auth_db_session.flush()

        created = await auth_service.create_internal_user(
            auth_db_session,
            user_id="internal-u1",
            username="internaluser",
            role_ids=[role.id],
        )
        assert created.status == "ACTIVE"

        from auth_service.crud.credential_crud import credential_crud

        await auth_service.disable_user(auth_db_session, "internal-u1")
        user = await auth_service.get_current_user(auth_db_session, "internal-u1")
        assert user.status == "DISABLED"
        credential = await credential_crud.get_by_user_id(auth_db_session, "internal-u1")
        assert credential is not None
        assert credential.locked_until is not None

        await auth_service.enable_user(auth_db_session, "internal-u1")
        user = await auth_service.get_current_user(auth_db_session, "internal-u1")
        assert user.status == "ACTIVE"
        credential = await credential_crud.get_by_user_id(auth_db_session, "internal-u1")
        assert credential is not None
        assert credential.locked_until is None

        await auth_service.delete_user(auth_db_session, "internal-u1")
        from shared.exceptions import ResourceNotFoundError

        with pytest.raises(ResourceNotFoundError):
            await auth_service.get_current_user(auth_db_session, "internal-u1")

    async def test_create_duplicate_user_raises(
        self, auth_db_session, seeded_auth_user, auth_security_env
    ) -> None:
        """重复 user_id 应抛出 BusinessRuleError。"""
        with pytest.raises(BusinessRuleError):
            await auth_service.create_internal_user(
                auth_db_session,
                user_id=seeded_auth_user["user_id"],
                username="other",
                role_ids=[],
            )

    async def test_create_user_invalid_role_id_raises(
        self, auth_db_session, auth_security_env
    ) -> None:
        """不存在的 role_id 应抛出 BusinessRuleError。"""
        with pytest.raises(BusinessRuleError):
            await auth_service.create_internal_user(
                auth_db_session,
                user_id="internal-bad-role",
                username="badroleuser",
                role_ids=[99999],
            )


@pytest.mark.unit
class TestAuthServiceMisc:
    """测试改密与服务登录。"""

    async def test_change_password(
        self, auth_db_session, seeded_auth_user, auth_security_env
    ) -> None:
        """旧密码正确时应能更新密码。"""
        await auth_service.change_password(
            auth_db_session,
            seeded_auth_user["user_id"],
            ChangePasswordRequest(old_password="SeedPass1", new_password="NewPass12"),
        )
        await auth_service.login(auth_db_session, seeded_auth_user["username"], "NewPass12")

    async def test_service_login(self, auth_db_session, auth_service_credentials) -> None:
        """正确 client 凭据应返回 service token。"""
        result = await auth_service.service_login(auth_db_session, "test-client", "test-secret")
        assert result.service_token
        payload = verify_token(result.service_token)
        assert payload["type"] == "service"

    async def test_service_login_invalid_credentials(
        self, auth_db_session, auth_service_credentials
    ) -> None:
        """错误凭据应抛出 ServiceCredentialInvalidError。"""
        with pytest.raises(ServiceCredentialInvalidError):
            await auth_service.service_login(auth_db_session, "test-client", "wrong")
