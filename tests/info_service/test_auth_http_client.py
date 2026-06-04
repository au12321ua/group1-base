"""Tests for the Auth Service HTTP client wrapper."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from info_service.services import auth_http_client
from info_service.services.auth_http_client import AuthServiceClient


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


@pytest.mark.unit
class TestAuthServiceClient:
    """Validate token lifecycle and request composition."""

    async def test_acquire_token_posts_credentials_and_sets_expiry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, object] = {}

        class FakeAsyncClient:
            def __init__(self, *, timeout: int) -> None:
                captured["timeout"] = timeout

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb) -> bool:
                return False

            async def post(self, url: str, json: dict) -> _DummyResponse:
                captured["url"] = url
                captured["json"] = json
                return _DummyResponse(
                    {"data": {"service_token": "svc-token", "expires_in": 100}}
                )

        monkeypatch.setattr(auth_http_client.httpx, "AsyncClient", FakeAsyncClient)
        monkeypatch.setattr(auth_http_client.time, "time", lambda: 1000.0)

        client = AuthServiceClient("http://auth.example", "client-id", "client-secret", timeout=7)
        token = await client._acquire_token()

        assert token == "svc-token"
        assert client._token_expires_at == 1080.0
        assert captured["timeout"] == 7
        assert captured["url"] == "http://auth.example/api/v1/auth/sys/login"
        assert captured["json"] == {
            "client_id": "client-id",
            "client_secret": "client-secret",
        }

    async def test_get_token_uses_cache_until_expiry(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        current_time = {"value": 50.0}
        client = AuthServiceClient("http://auth.example", "client-id", "client-secret")
        client._token = "cached-token"
        client._token_expires_at = 100.0

        monkeypatch.setattr(auth_http_client.time, "time", lambda: current_time["value"])
        acquire_mock = AsyncMock(return_value="fresh-token")
        monkeypatch.setattr(client, "_acquire_token", acquire_mock)

        assert await client._get_token() == "cached-token"
        acquire_mock.assert_not_awaited()

        current_time["value"] = 120.0
        assert await client._get_token() == "fresh-token"
        acquire_mock.assert_awaited_once()

    async def test_request_attaches_authorization_header(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, object] = {}

        class FakeAsyncClient:
            def __init__(self, *, timeout: int) -> None:
                captured["timeout"] = timeout

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb) -> bool:
                return False

            async def request(
                self, method: str, url: str, headers: dict[str, str], **kwargs
            ) -> httpx.Response:
                captured["method"] = method
                captured["url"] = url
                captured["headers"] = headers
                captured["kwargs"] = kwargs
                return httpx.Response(200, json={"ok": True})

        monkeypatch.setattr(auth_http_client.httpx, "AsyncClient", FakeAsyncClient)

        client = AuthServiceClient("http://auth.example", "client-id", "client-secret", timeout=9)
        monkeypatch.setattr(client, "_get_token", AsyncMock(return_value="svc-token"))

        response = await client._request(
            "POST",
            "/api/v1/internal/users",
            headers={"X-Test": "1"},
            json={"user_id": "u1"},
        )

        assert response.status_code == 200
        assert captured["timeout"] == 9
        assert captured["method"] == "POST"
        assert captured["url"] == "http://auth.example/api/v1/internal/users"
        assert captured["headers"] == {
            "X-Test": "1",
            "Authorization": "Bearer svc-token",
        }
        assert captured["kwargs"] == {"json": {"user_id": "u1"}}

    async def test_internal_helpers_prefix_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = AuthServiceClient("http://auth.example", "client-id", "client-secret")
        request_mock = AsyncMock(return_value=httpx.Response(204))
        monkeypatch.setattr(client, "_request", request_mock)

        await client.post_internal("/users", json={"user_id": "u1"})
        await client.delete_internal("/users/u1")

        assert request_mock.await_args_list[0].args == ("POST", "/api/v1/internal/users")
        assert request_mock.await_args_list[0].kwargs == {"json": {"user_id": "u1"}}
        assert request_mock.await_args_list[1].args == ("DELETE", "/api/v1/internal/users/u1")

    def test_get_auth_service_client_returns_singleton(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(auth_http_client, "_auth_client", None)
        monkeypatch.setattr(
            "info_service.core.config.get_info_settings",
            lambda: SimpleNamespace(
                auth_service_url="http://auth.example",
                auth_service_client_id="client-id",
                auth_service_client_secret="client-secret",
                auth_service_timeout=11,
            ),
        )

        first = auth_http_client.get_auth_service_client()
        second = auth_http_client.get_auth_service_client()

        assert first is second
        assert first._base_url == "http://auth.example"
        assert first._timeout == 11
