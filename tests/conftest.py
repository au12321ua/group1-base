"""Top-level test configuration — shared fixtures for both services."""

import os

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

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
        "academic_calendars",
        "base_info_items",
        "file_resources",
    }
)

_AUDIT_TABLES: frozenset[str] = frozenset(
    {
        "audit_logs",
        "dead_letter_queue",
        "operation_logs",
    }
)


def _make_create_tables(table_names: frozenset[str]):
    """返回一个同步函数，只在目标连接上创建指定名称的表。"""

    def _create(sync_conn) -> None:
        tables = [t for t in SQLModel.metadata.sorted_tables if t.name in table_names]
        SQLModel.metadata.create_all(sync_conn, tables=tables)

    return _create


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
        await conn.run_sync(_make_create_tables(_AUTH_TABLES))
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
        await conn.run_sync(_make_create_tables(_INFO_TABLES))
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
        await conn.run_sync(_make_create_tables(_AUDIT_TABLES))
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
    from sqlmodel import SQLModel

    from auth_service.main import _AUDIT_TABLES, _AUTH_TABLES, app, audit_engine, engine

    async with engine.begin() as conn:
        tables = [t for t in SQLModel.metadata.sorted_tables if t.name in _AUTH_TABLES]
        await conn.run_sync(
            lambda sync_conn: SQLModel.metadata.create_all(sync_conn, tables=tables)
        )

    async with audit_engine.begin() as conn:
        tables = [t for t in SQLModel.metadata.sorted_tables if t.name in _AUDIT_TABLES]
        await conn.run_sync(
            lambda sync_conn: SQLModel.metadata.create_all(sync_conn, tables=tables)
        )

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_client_info():
    """httpx AsyncClient connected directly to the Info Service FastAPI app."""
    from httpx import ASGITransport, AsyncClient
    from sqlmodel import SQLModel

    from info_service.main import app, audit_engine, info_engine

    async with info_engine.begin() as conn:
        tables = [t for t in SQLModel.metadata.sorted_tables if t.name in _INFO_TABLES]
        await conn.run_sync(
            lambda sync_conn: SQLModel.metadata.create_all(sync_conn, tables=tables)
        )

    async with audit_engine.begin() as conn:
        tables = [t for t in SQLModel.metadata.sorted_tables if t.name in _AUDIT_TABLES]
        await conn.run_sync(
            lambda sync_conn: SQLModel.metadata.create_all(sync_conn, tables=tables)
        )

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
