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
