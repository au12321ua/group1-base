"""Tests for shared/database.py — get_db dependency."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from auth_service.models.user import User, UserStatus


@pytest.fixture
def get_db():
    """Import get_db after it exists."""
    from shared.database import create_get_db

    return create_get_db


@pytest.mark.unit
class TestCreateGetDb:
    """Tests for the create_get_db factory function."""

    async def test_returns_async_generator_function(self, get_db, auth_db_engine):
        """create_get_db returns a callable."""
        dep = get_db(auth_db_engine)
        assert callable(dep)

    async def test_get_db_yields_valid_session(self, get_db, auth_db_engine):
        """The generated dependency yields an AsyncSession."""
        dep = get_db(auth_db_engine)

        gen = dep()
        assert isinstance(gen, AsyncGenerator)

        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)

        # Clean up
        try:
            await gen.aclose()
        except StopAsyncIteration:
            pass

    async def test_session_can_perform_crud(self, get_db, auth_db_engine):
        """Basic CRUD through the yielded session works."""
        dep = get_db(auth_db_engine)
        gen = dep()
        session = await gen.__anext__()

        user = User(user_id="u-test-001", username="testuser", status=UserStatus.ACTIVE)
        session.add(user)
        await session.flush()

        result = await session.exec(select(User).where(User.user_id == "u-test-001"))
        found = result.first()
        assert found is not None
        assert found.username == "testuser"

        try:
            await gen.aclose()
        except StopAsyncIteration:
            pass

    async def test_session_commit_persists_data(self, get_db, auth_db_engine):
        """Data committed through the session persists across sessions."""
        dep = get_db(auth_db_engine)

        # Session 1: create and commit
        gen1 = dep()
        session1 = await gen1.__anext__()
        user = User(user_id="u-test-002", username="persistuser", status=UserStatus.ACTIVE)
        session1.add(user)
        await session1.commit()

        try:
            await gen1.aclose()
        except StopAsyncIteration:
            pass

        # Session 2: read back
        gen2 = dep()
        session2 = await gen2.__anext__()
        result = await session2.exec(select(User).where(User.user_id == "u-test-002"))
        found = result.first()
        assert found is not None
        assert found.username == "persistuser"

        try:
            await gen2.aclose()
        except StopAsyncIteration:
            pass

    async def test_session_rollback_discards_changes(self, get_db, auth_db_engine):
        """Uncommitted changes are discarded after rollback."""
        dep = get_db(auth_db_engine)

        # Create user but rollback
        gen1 = dep()
        session1 = await gen1.__anext__()
        user = User(user_id="u-rollback", username="rollbackuser", status=UserStatus.ACTIVE)
        session1.add(user)
        await session1.rollback()

        try:
            await gen1.aclose()
        except StopAsyncIteration:
            pass

        # Verify user was not persisted
        gen2 = dep()
        session2 = await gen2.__anext__()
        result = await session2.exec(select(User).where(User.user_id == "u-rollback"))
        found = result.first()
        assert found is None

        try:
            await gen2.aclose()
        except StopAsyncIteration:
            pass

    async def test_different_engines_are_independent(self, get_db, auth_db_engine, info_db_engine):
        """Dep instances for different engines work independently."""
        auth_dep = get_db(auth_db_engine)
        info_dep = get_db(info_db_engine)

        auth_gen = auth_dep()
        info_gen = info_dep()
        auth_session = await auth_gen.__anext__()
        info_session = await info_gen.__anext__()

        # Auth session can work with Auth tables
        user = User(user_id="u-cross", username="crossuser", status=UserStatus.ACTIVE)
        auth_session.add(user)
        await auth_session.flush()
        assert user.id is not None

        # Info session cannot see Auth tables (would raise OperationalError)
        with pytest.raises(Exception):
            await info_session.exec(select(User).where(User.user_id == "u-cross"))

        try:
            await auth_gen.aclose()
        except StopAsyncIteration:
            pass
        try:
            await info_gen.aclose()
        except StopAsyncIteration:
            pass
