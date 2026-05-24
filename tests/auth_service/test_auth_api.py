"""Integration tests for Auth Service HTTP endpoints."""

import pytest

from auth_service.core.config import get_auth_settings


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
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["data"]["user_id"] == user_id

    async def test_public_key(self, async_client_auth, auth_security_env) -> None:
        """GET /auth/public-key 应返回 JWKS。"""
        resp = await async_client_auth.get("/api/v1/auth/public-key")
        assert resp.status_code == 200
        assert resp.json()["data"]["keys"]

    async def test_service_login(self, async_client_auth, auth_service_credentials) -> None:
        """POST /auth/sys/login 在正确凭据下应成功。"""
        settings = get_auth_settings()
        resp = await async_client_auth.post(
            "/api/v1/auth/sys/login",
            json={
                "client_id": settings.service_client_id,
                "client_secret": settings.service_client_secret,
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
        )
        assert create_resp.status_code == 201

        disable_resp = await async_client_auth.post(f"/api/v1/internal/users/{user_id}/disable")
        assert disable_resp.status_code == 200

        disabled_login_resp = await async_client_auth.post(
            "/api/v1/auth/login",
            json={"username": username, "password": settings.default_initial_password},
        )
        assert disabled_login_resp.status_code == 423
        assert disabled_login_resp.json()["code"] == 1003

        enable_resp = await async_client_auth.post(f"/api/v1/internal/users/{user_id}/enable")
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
        )
        assert sync_resp.status_code == 200
        assert sync_resp.json()["data"]["user_id"] == user_id
        assert sync_resp.json()["data"]["role_ids"] == []

        verify_refresh_resp = await async_client_auth.post(
            "/api/v1/internal/verify",
            json={"token": refresh_token},
        )
        assert verify_refresh_resp.status_code == 401
        assert verify_refresh_resp.json()["code"] == 1001

        delete_resp = await async_client_auth.delete(f"/api/v1/internal/users/{user_id}")
        assert delete_resp.status_code == 204
