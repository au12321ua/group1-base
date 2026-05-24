"""API-layer dependencies (lazy DB import to avoid circular import with main)."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_auth_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an Auth DB session (commits on success)."""
    from auth_service.main import get_db

    async for session in get_db():
        yield session


AuthDbSession = Annotated[AsyncSession, Depends(get_auth_db_session)]
