"""Top-level test configuration — shared fixtures for both services."""

import os

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from shared.database import create_tables
from shared.models.audit_log import AUDIT_TABLE_NAMES
from tests.utils import create_test_service_token

# ---------------------------------------------------------------------------
# Test env defaults
# Force async SQLite URLs so importing main.py never creates sync drivers.
# Use assignment (not setdefault): shell may still export sync URLs from alembic.
# ---------------------------------------------------------------------------
os.environ["ENV"] = "test"
os.environ["AUTH_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["INFO_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AUDIT_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("UPLOAD_DIR", "/tmp/stss-test-uploads")

# ---------------------------------------------------------------------------
# Import all models so their tables are registered in SQLModel.metadata.
# Each engine fixture then filters to only create the tables that belong to
# its own service, keeping Auth DB / Info DB / Audit DB properly separated.
# ---------------------------------------------------------------------------
import auth_service.models.credential  # noqa: F401
import auth_service.models.permission  # noqa: F401
import auth_service.models.role  # noqa: F401
import auth_service.models.session  # noqa: F401
import auth_service.models.token  # noqa: F401
import auth_service.models.user  # noqa: F401
import info_service.models.academic_calendar  # noqa: F401
import info_service.models.audit_log  # noqa: F401
import info_service.models.base_info_item  # noqa: F401
import info_service.models.classroom  # noqa: F401
import info_service.models.course  # noqa: F401
import info_service.models.course_offering  # noqa: F401
import info_service.models.course_prerequisite  # noqa: F401
import info_service.models.course_schedule  # noqa: F401
import info_service.models.file_resource  # noqa: F401
import info_service.models.teacher_assignment  # noqa: F401
import info_service.models.training_program  # noqa: F401
import info_service.models.user  # noqa: F401
import info_service.models.user_profile  # noqa: F401

# ---------------------------------------------------------------------------
# Per-service table name sets — each engine only creates the tables that
# belong to its service, mirroring the auth.db / info.db / audit.db split.
# ---------------------------------------------------------------------------
_AUTH_TABLES: frozenset[str] = frozenset(
    {
        "users",
        "credentials",
        "roles",
        "user_roles",
        "permissions",
        "role_permissions",
        "tokens",
        "authentication_sessions",
    }
)

_INFO_TABLES: frozenset[str] = frozenset(
    {
        "users_info",
        "user_profiles",
        "courses",
        "course_offerings",
        "course_prerequisites",
        "course_schedules",
        "teacher_course_assignments",
        "classrooms",
        "training_programs",
        "training_program_courses",
        "academic_calendars",
        "base_info_items",
        "file_resources",
    }
)

@pytest.fixture(scope="session")
def anyio_backend():
    """Explicitly set the async backend to asyncio."""
    return "asyncio"


# ===========================================================================
# Database fixtures — Auth Service
# ===========================================================================


@pytest.fixture(scope="function")
async def auth_db_engine():
    """In-memory SQLite engine for Auth DB — only Auth Service tables are created."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(create_tables, _AUTH_TABLES)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def auth_db_session(auth_db_engine):
    """AsyncSession for Auth DB — fresh engine per test already ensures isolation."""
    async with AsyncSession(auth_db_engine, expire_on_commit=False) as session:
        yield session


# ===========================================================================
# Database fixtures — Info Service
# ===========================================================================


@pytest.fixture(scope="function")
async def info_db_engine():
    """In-memory SQLite engine for Info DB — only Info Service tables are created."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(create_tables, _INFO_TABLES)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def info_db_session(info_db_engine):
    """AsyncSession for Info DB — fresh engine per test already ensures isolation."""
    async with AsyncSession(info_db_engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(scope="function")
async def audit_db_engine():
    """In-memory SQLite engine for Audit DB — only Audit tables are created."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(create_tables, AUDIT_TABLE_NAMES)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def audit_db_session(audit_db_engine):
    """AsyncSession for Audit DB — fresh engine per test already ensures isolation."""
    async with AsyncSession(audit_db_engine, expire_on_commit=False) as session:
        yield session


# ===========================================================================
# HTTP client fixtures
# ===========================================================================


@pytest.fixture
async def async_client_auth():
    """httpx AsyncClient connected directly to the Auth Service FastAPI app."""
    from httpx import ASGITransport, AsyncClient

    from auth_service.main import _AUTH_TABLES, app, audit_engine, engine
    from shared.database import create_tables
    from shared.models.audit_log import AUDIT_TABLE_NAMES

    async with engine.begin() as conn:
        await conn.run_sync(create_tables, _AUTH_TABLES)

    async with audit_engine.begin() as conn:
        await conn.run_sync(create_tables, AUDIT_TABLE_NAMES)

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_client_info():
    """httpx AsyncClient connected directly to the Info Service FastAPI app."""
    from httpx import ASGITransport, AsyncClient

    from info_service.main import app, audit_engine, info_engine

    async with info_engine.begin() as conn:
        await conn.run_sync(create_tables, _INFO_TABLES)

    async with audit_engine.begin() as conn:
        await conn.run_sync(create_tables, AUDIT_TABLE_NAMES)

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class _AuthServiceBridgeClient:
    """Bridge Info-side internal HTTP calls to the local Auth ASGI app."""

    def __init__(self, app) -> None:
        self._transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
        self._headers = {
            "Authorization": f"Bearer {create_test_service_token()}",
        }

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        headers = {**self._headers, **kwargs.pop("headers", {})}
        async with httpx.AsyncClient(
            transport=self._transport,
            base_url="http://auth-bridge",
        ) as client:
            return await client.request(
                method,
                f"/api/v1/internal{path}",
                headers=headers,
                **kwargs,
            )

    async def post_internal(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("POST", path, **kwargs)

    async def delete_internal(self, path: str, **kwargs) -> httpx.Response:
        return await self._request("DELETE", path, **kwargs)


@pytest.fixture
async def auth_service_bridge(async_client_auth, monkeypatch: pytest.MonkeyPatch):
    """Patch Info Service cross-service client calls to use the local Auth app."""
    from auth_service.main import app as auth_app
    from info_service.services import auth_client, auth_http_client

    bridge = _AuthServiceBridgeClient(auth_app)
    monkeypatch.setattr(auth_http_client, "get_auth_service_client", lambda: bridge)
    monkeypatch.setattr(auth_client, "get_auth_service_client", lambda: bridge)
    yield bridge
