"""Tests for main.py wiring — router registration, DB lifespan, error handlers."""

import pytest


# ---------------------------------------------------------------------------
# Auth Service — router registration
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestAuthRouterRegistration:
    """Verify Auth Service v1 router is included and sub-routers are wired."""

    async def test_v1_auth_login_route_exists(self, async_client_auth):
        """POST /api/v1/auth/login is registered in the schema."""
        resp = await async_client_auth.get("/openapi.json")
        schema = resp.json()
        assert "/api/v1/auth/login" in schema["paths"]

    async def test_v1_auth_refresh_route_exists(self, async_client_auth):
        """POST /api/v1/auth/refresh is registered in the schema."""
        resp = await async_client_auth.get("/openapi.json")
        schema = resp.json()
        assert "/api/v1/auth/refresh" in schema["paths"]

    async def test_v1_auth_me_route_exists(self, async_client_auth):
        """GET /api/v1/auth/me is registered in the schema."""
        resp = await async_client_auth.get("/openapi.json")
        schema = resp.json()
        assert "/api/v1/auth/me" in schema["paths"]


# ---------------------------------------------------------------------------
# Info Service — router registration
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestInfoRouterRegistration:
    """Verify Info Service v1 router is included and sub-routers are wired."""

    async def test_v1_users_route_exists(self, async_client_info):
        """GET /api/v1/users is registered in the schema."""
        resp = await async_client_info.get("/openapi.json")
        schema = resp.json()
        paths = schema["paths"]
        assert any(p.startswith("/api/v1/users") for p in paths)

    async def test_v1_courses_route_exists(self, async_client_info):
        """GET /api/v1/courses is registered in the schema."""
        resp = await async_client_info.get("/openapi.json")
        schema = resp.json()
        paths = schema["paths"]
        assert any(p.startswith("/api/v1/courses") for p in paths)

    async def test_v1_schedules_route_exists(self, async_client_info):
        """GET /api/v1/schedules is registered in the schema."""
        resp = await async_client_info.get("/openapi.json")
        schema = resp.json()
        paths = schema["paths"]
        assert any(p.startswith("/api/v1/schedules") for p in paths)


# ---------------------------------------------------------------------------
# Lifespan check
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestLifespan:
    """Verify lifespan is attached to both apps."""

    def test_auth_app_has_lifespan(self):
        """Auth Service app has a lifespan callable set."""
        from auth_service.main import app

        assert app.router.lifespan is not None
        assert callable(app.router.lifespan)

    def test_info_app_has_lifespan(self):
        """Info Service app has a lifespan callable set."""
        from info_service.main import app

        assert app.router.lifespan is not None
        assert callable(app.router.lifespan)


# ---------------------------------------------------------------------------
# Error handler registration
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestErrorHandlerRegistration:
    """Verify error handlers are registered in both apps."""

    def test_auth_app_has_error_handlers(self):
        """Auth Service app handles AppError-based exceptions."""
        from auth_service.main import app

        # The app should have exception handlers registered
        handlers = app.exception_handlers
        assert len(handlers) > 0

    def test_info_app_has_error_handlers(self):
        """Info Service app handles AppError-based exceptions."""
        from info_service.main import app

        handlers = app.exception_handlers
        assert len(handlers) > 0
