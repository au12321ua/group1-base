"""API-layer dependencies for Info Service."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_info_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an Info DB session backed by the service database dependency."""
    from info_service.main import get_info_db

    async for session in get_info_db():
        yield session


InfoDbSession = Annotated[AsyncSession, Depends(get_info_db_session)]
