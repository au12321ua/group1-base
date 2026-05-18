"""Tests for shared/error_handlers.py — AppException → APIResponse mapping."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from shared.exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ResourceNotFoundError,
    TokenExpiredError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _builder():
    """Import and return `register_error_handlers` from `shared.error_handlers`."""
    from shared.error_handlers import register_error_handlers

    return register_error_handlers


_EXCEPTIONS: dict[str, tuple[type[AppError], AppError, int]] = {
    "AppError": (AppError, AppError(code=9999, message="test error", detail="test detail"), 500),
    "AuthenticationError": (AuthenticationError, AuthenticationError(), 401),
    "AuthorizationError": (AuthorizationError, AuthorizationError(), 403),
    "ResourceNotFoundError": (
        ResourceNotFoundError,
        ResourceNotFoundError(resource="User", identifier="123"),
        404,
    ),
    "BusinessRuleError": (BusinessRuleError, BusinessRuleError(message="duplicate entry"), 409),
    "AccountLockedError": (AccountLockedError, AccountLockedError(), 423),
    "AccountDisabledError": (AccountDisabledError, AccountDisabledError(), 401),
    "TokenExpiredError": (TokenExpiredError, TokenExpiredError(), 401),
}


def make_test_app():
    app = FastAPI()
    register = _builder()
    register(app)

    @app.get("/raise/{exc_type}")
    async def raise_exc(exc_type: str):
        raise _EXCEPTIONS[exc_type][1]

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
async def client():
    transport = ASGITransport(app=make_test_app())  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestErrorHandlerRegistration:
    def test_import_exists(self):
        """register_error_handlers is importable from shared.error_handlers."""
        register = _builder()
        assert callable(register)


class TestAppExceptionToApiResponse:
    @pytest.mark.parametrize(
        "exc_type, exc_instance, expected_status",
        [
            pytest.param(cls, inst, status, id=name)
            for name, (cls, inst, status) in _EXCEPTIONS.items()
        ],
    )
    async def test_status_code(self, client, exc_type, exc_instance, expected_status):
        """Each AppError subclass maps to the correct HTTP status code."""
        resp = await client.get(f"/raise/{exc_type.__name__}")
        assert resp.status_code == expected_status

    @pytest.mark.parametrize(
        "exc_type, exc_instance, expected_status",
        [
            pytest.param(cls, inst, status, id=name)
            for name, (cls, inst, status) in _EXCEPTIONS.items()
        ],
    )
    async def test_response_body_has_code_and_message(
        self, client, exc_type, exc_instance, expected_status
    ):
        """Response body contains code and message from the AppError."""
        resp = await client.get(f"/raise/{exc_type.__name__}")
        body = resp.json()
        assert "code" in body
        assert body["code"] == exc_instance.code
        assert "message" in body
        assert body["message"] == exc_instance.message

    @pytest.mark.parametrize(
        "exc_type, exc_instance, expected_status",
        [
            pytest.param(cls, inst, status, id=name)
            for name, (cls, inst, status) in _EXCEPTIONS.items()
        ],
    )
    async def test_errors_field(self, client, exc_type, exc_instance, expected_status):
        """errors field is included when detail is non-empty."""
        resp = await client.get(f"/raise/{exc_type.__name__}")
        body = resp.json()
        if exc_instance.detail:
            assert body["errors"] == [{"detail": exc_instance.detail}]
        else:
            # errors may be absent or None
            assert body.get("errors") is None or body.get("errors") == []

    async def test_unknown_app_error_returns_500(self, client):
        """An AppError subclass not explicitly mapped defaults to 500."""

        class CustomAppError(AppError):
            pass

        @client._transport.app.get("/raise-custom")  # type: ignore[union-attr]
        async def raise_custom():
            raise CustomAppError(code=7777, message="custom error")

        resp = await client.get("/raise-custom")
        assert resp.status_code == 500
        body = resp.json()
        assert body["code"] == 7777
        assert body["message"] == "custom error"
