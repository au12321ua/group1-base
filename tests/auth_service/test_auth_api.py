"""Integration tests for Auth Service HTTP endpoints."""

import pytest

from auth_service.core.config import get_auth_settings
from tests.utils import build_auth_header, create_test_service_token


def _svc_headers() -> dict[str, str]:
    """Build service token auth headers for internal endpoint calls."""
    return build_auth_header(create_test_service_token())


@pytest.mark.integration
class TestAuthAPI:
    """测试 /api/v1/auth 与 /api/v1/internal 路由（经 ASGI 客户端）。"""

    async def test_internal_create_login_me_and_verify(
        self, async_client_auth, auth_security_env
    ) -> None:
        """内部创建用户 → 登录 → /me → /internal/verify 全链路。"""
        settings = get_auth_settings()
        user_id = "api-int-u1"
        username = "apiintuser"

        create_resp = await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": user_id, "username": username, "role_ids": []},
            headers=_svc_headers(),
        )
        assert create_resp.status_code == 201
        assert create_resp.json()["data"]["user_id"] == user_id

        login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": settings.default_initial_password},
        )
        assert login_resp.status_code == 200
        login_body = login_resp.json()
        assert login_body["code"] == 0
        access = login_body["data"]["access_token"]

        me_resp = await async_client_auth.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["data"]["user_id"] == user_id

        verify_resp = await async_client_auth.post(
            "/api/v1/internal/verify",
            json={"token": access},
            headers=_svc_headers(),
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["data"]["user_id"] == user_id

    async def test_service_login(self, async_client_auth, auth_service_credentials) -> None:
        """POST /auth/sys/login 在正确凭据下应成功。"""
        settings = get_auth_settings()
        cfg = list(settings.service_client_configs.values())[0]
        resp = await async_client_auth.post(
            "/api/v1/auth/sys/login",
            json={
                "client_id": cfg["id"],
                "client_secret": cfg["secret"],
            },
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["service_token"]

    async def test_refresh_and_logout(
        self, async_client_auth, auth_security_env
    ) -> None:
        """刷新 token 与登出应成功。"""
        settings = get_auth_settings()
        await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": "api-ref-u1", "username": "apirefuser", "role_ids": []},
            headers=_svc_headers(),
        )
        login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": "apirefuser", "password": settings.default_initial_password},
        )
        refresh_token = login_resp.json()["data"]["refresh_token"]

        refresh_resp = await async_client_auth.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_resp.status_code == 200
        new_refresh = refresh_resp.json()["data"]["refresh_token"]

        logout_resp = await async_client_auth.post(
            "/api/v1/auth/logout",
            json={"refresh_token": new_refresh},
        )
        assert logout_resp.status_code == 200

    async def test_change_password_flow(self, async_client_auth, auth_security_env) -> None:
        """创建用户后应支持改密，且新密码可登录旧密码失效。"""
        settings = get_auth_settings()
        user_id = "api-pwd-u1"
        username = "apipwduser"

        create_resp = await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": user_id, "username": username, "role_ids": []},
            headers=_svc_headers(),
        )
        assert create_resp.status_code == 201

        login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": settings.default_initial_password},
        )
        assert login_resp.status_code == 200
        access = login_resp.json()["data"]["access_token"]

        change_resp = await async_client_auth.post(
            "/api/v1/auth/change-password",
            json={
                "old_password": settings.default_initial_password,
                "new_password": "NewPass123",
            },
            headers={"Authorization": f"Bearer {access}"},
        )
        assert change_resp.status_code == 200

        old_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": settings.default_initial_password},
        )
        assert old_login_resp.status_code == 401
        assert old_login_resp.json()["code"] == 1001

        new_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "NewPass123"},
        )
        assert new_login_resp.status_code == 200
        assert new_login_resp.json()["data"]["user_id"] == user_id

    async def test_internal_user_lifecycle(self, async_client_auth, auth_security_env) -> None:
        """内部用户接口应支持禁用/启用/角色同步/删除全生命周期。"""
        settings = get_auth_settings()
        user_id = "api-life-u1"
        username = "apilifeuser"

        create_resp = await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": user_id, "username": username, "role_ids": []},
            headers=_svc_headers(),
        )
        assert create_resp.status_code == 201

        disable_resp = await async_client_auth.post(
            f"/api/v1/internal/users/{user_id}/disable",
            headers=_svc_headers(),
        )
        assert disable_resp.status_code == 200

        disabled_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": settings.default_initial_password},
        )
        assert disabled_login_resp.status_code == 423
        assert disabled_login_resp.json()["code"] == 1003

        enable_resp = await async_client_auth.post(
            f"/api/v1/internal/users/{user_id}/enable",
            headers=_svc_headers(),
        )
        assert enable_resp.status_code == 200

        enabled_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": settings.default_initial_password},
        )
        assert enabled_login_resp.status_code == 200
        assert enabled_login_resp.json()["data"]["user_id"] == user_id
        refresh_token = enabled_login_resp.json()["data"]["refresh_token"]

        sync_resp = await async_client_auth.post(
            f"/api/v1/internal/users/{user_id}/roles",
            json={"role_ids": []},
            headers=_svc_headers(),
        )
        assert sync_resp.status_code == 200
        assert sync_resp.json()["data"]["user_id"] == user_id
        assert sync_resp.json()["data"]["role_ids"] == []

        verify_refresh_resp = await async_client_auth.post(
            "/api/v1/internal/verify",
            json={"token": refresh_token},
            headers=_svc_headers(),
        )
        assert verify_refresh_resp.status_code == 401
        assert verify_refresh_resp.json()["code"] == 1001

        delete_resp = await async_client_auth.delete(
            f"/api/v1/internal/users/{user_id}",
            headers=_svc_headers(),
        )
        assert delete_resp.status_code == 204


@pytest.mark.integration
class TestInternalEndpointsAuth:
    """测试 /api/v1/internal 端点的 Service Token 鉴权守卫。"""

    # ── 辅助方法 ──────────────────────────────────────────────

    @staticmethod
    async def _login_and_get_access(async_client_auth) -> str:
        """创建用户并登录，返回 access token。"""
        from auth_service.core.config import get_auth_settings

        settings = get_auth_settings()
        uid = "auth-test-u1"
        uname = "authtestuser"

        await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": uid, "username": uname, "role_ids": []},
            headers=_svc_headers(),
        )
        resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": uname, "password": settings.default_initial_password},
        )
        return resp.json()["data"]["access_token"]

    # ── 无 Token ───────────────────────────────────────────────

    _NO_TOKEN_ENDPOINTS = [
        ("POST", "/api/v1/internal/verify", {"token": "dummy"}),
        ("POST", "/api/v1/internal/users", {"user_id": "u1", "username": "x", "role_ids": []}),
        ("POST", "/api/v1/internal/users/u1/disable", None),
        ("POST", "/api/v1/internal/users/u1/enable", None),
        ("POST", "/api/v1/internal/users/u1/roles", {"role_ids": []}),
        ("DELETE", "/api/v1/internal/users/u1", None),
    ]

    @pytest.mark.parametrize("method,url,body", _NO_TOKEN_ENDPOINTS)
    async def test_no_token_returns_401(
        self, method, url, body, async_client_auth, auth_security_env
    ) -> None:
        """缺少 Service Token 的请求应返回 401。"""
        resp = await async_client_auth.request(method, url, json=body)
        assert resp.status_code == 401

    # ── Access Token 冒充 Service Token ────────────────────────

    _ACCESS_TOKEN_ENDPOINTS = [
        ("POST", "/api/v1/internal/verify", {"token": "dummy"}),
        ("POST", "/api/v1/internal/users", {"user_id": "u2", "username": "y", "role_ids": []}),
        ("POST", "/api/v1/internal/users/u2/disable", None),
        ("POST", "/api/v1/internal/users/u2/enable", None),
        ("POST", "/api/v1/internal/users/u2/roles", {"role_ids": []}),
        ("DELETE", "/api/v1/internal/users/u2", None),
    ]

    @pytest.mark.parametrize("method,url,body", _ACCESS_TOKEN_ENDPOINTS)
    async def test_access_token_returns_401(
        self, method, url, body, async_client_auth, auth_security_env
    ) -> None:
        """使用 Access Token（非 Service Token）调用内部接口应返回 401。"""
        access_token = await self._login_and_get_access(async_client_auth)
        headers = build_auth_header(access_token)
        resp = await async_client_auth.request(method, url, json=body, headers=headers)
        assert resp.status_code == 401

    # ── 合法 Service Token ─────────────────────────────────────

    async def test_service_token_allows_verify(
        self, async_client_auth, auth_security_env
    ) -> None:
        """合法 Service Token 下 /internal/verify 应成功。"""
        access_token = await self._login_and_get_access(async_client_auth)
        headers = _svc_headers()
        resp = await async_client_auth.post(
            "/api/v1/internal/verify",
            json={"token": access_token},
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_service_token_allows_create_user(
        self, async_client_auth, auth_security_env
    ) -> None:
        """合法 Service Token 下 /internal/users 应创建成功。"""
        headers = _svc_headers()
        resp = await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": "svc-u1", "username": "svcuser", "role_ids": []},
            headers=headers,
        )
        assert resp.status_code == 201

    async def test_service_token_allows_disable_enable(
        self, async_client_auth, auth_security_env
    ) -> None:
        """合法 Service Token 下 disable/enable 应成功。"""
        headers = _svc_headers()
        await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": "svc-u2", "username": "svcuser2", "role_ids": []},
            headers=headers,
        )
        dis = await async_client_auth.post(
            "/api/v1/internal/users/svc-u2/disable", headers=headers
        )
        assert dis.status_code == 200
        en = await async_client_auth.post(
            "/api/v1/internal/users/svc-u2/enable", headers=headers
        )
        assert en.status_code == 200

    async def test_service_token_allows_sync_roles(
        self, async_client_auth, auth_security_env
    ) -> None:
        """合法 Service Token 下角色同步应成功。"""
        headers = _svc_headers()
        await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": "svc-u3", "username": "svcuser3", "role_ids": []},
            headers=headers,
        )
        resp = await async_client_auth.post(
            "/api/v1/internal/users/svc-u3/roles",
            json={"role_ids": []},
            headers=headers,
        )
        assert resp.status_code == 200

    async def test_service_token_allows_delete(
        self, async_client_auth, auth_security_env
    ) -> None:
        """合法 Service Token 下删除用户应返回 204。"""
        headers = _svc_headers()
        await async_client_auth.post(
            "/api/v1/internal/users",
            json={"user_id": "svc-u4", "username": "svcuser4", "role_ids": []},
            headers=headers,
        )
        resp = await async_client_auth.delete(
            "/api/v1/internal/users/svc-u4", headers=headers
        )
        assert resp.status_code == 204
