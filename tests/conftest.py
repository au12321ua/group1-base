"""Top-level test configuration — shared fixtures for both services."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# ---------------------------------------------------------------------------
# Import all models so their tables are registered in SQLModel.metadata.
# Using SQLModel.metadata.create_all is the pragmatic approach — it creates
# tables for all imported models in each test database, which is harmless
# for in-memory SQLite.
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


@pytest.fixture(scope="session")
def anyio_backend():
    """Explicitly set the async backend to asyncio."""
    return "asyncio"


# ===========================================================================
# Database fixtures — Auth Service
# ===========================================================================


@pytest.fixture(scope="function")
async def auth_db_engine():
    """In-memory SQLite engine for Auth DB — tables created once per test."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def auth_db_session(auth_db_engine):
    """AsyncSession for Auth DB — rolled back after each test for isolation."""
    async with AsyncSession(auth_db_engine, expire_on_commit=False) as session:
        async with session.begin() as trans:
            yield session
            await trans.rollback()


# ===========================================================================
# Database fixtures — Info Service
# ===========================================================================


@pytest.fixture(scope="function")
async def info_db_engine():
    """In-memory SQLite engine for Info DB — tables created once per test."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def info_db_session(info_db_engine):
    """AsyncSession for Info DB — rolled back after each test for isolation."""
    async with AsyncSession(info_db_engine, expire_on_commit=False) as session:
        async with session.begin() as trans:
            yield session
            await trans.rollback()


@pytest.fixture(scope="function")
async def audit_db_engine():
    """In-memory SQLite engine for Audit DB — tables created once per test."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def audit_db_session(audit_db_engine):
    """AsyncSession for Audit DB — rolled back after each test for isolation."""
    async with AsyncSession(audit_db_engine, expire_on_commit=False) as session:
        async with session.begin() as trans:
            yield session
            await trans.rollback()


# ===========================================================================
# HTTP client fixtures
# ===========================================================================


@pytest.fixture
async def async_client_auth():
    """httpx AsyncClient connected directly to the Auth Service FastAPI app."""
    from httpx import ASGITransport, AsyncClient

    from auth_service.main import app

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_client_info():
    """httpx AsyncClient connected directly to the Info Service FastAPI app."""
    from httpx import ASGITransport, AsyncClient

    from info_service.main import app

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
