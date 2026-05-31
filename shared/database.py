"""Database session dependency for FastAPI.

Provides create_get_db, a factory that returns an async generator suitable
for use with fastapi.Depends(). Each service creates its own get_db from
its own AsyncEngine, keeping auth.db / info.db / audit.db independent.
"""

from collections.abc import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession


def create_get_db(engine: AsyncEngine) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    """Create a FastAPI database session dependency.

    Returns an async callable that yields an AsyncSession bound to the
    given engine. On successful use the session is committed; on exception
    it is rolled back; in all cases the session is closed.

    Usage::

        from shared.database import create_get_db

        engine_auth = create_async_engine("sqlite+aiosqlite:///auth.db")
        get_auth_db = create_get_db(engine_auth)

        @router.get("/users")
        async def list_users(db: Annotated[AsyncSession, Depends(get_auth_db)]):
            ...
    """

    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return get_db
