"""Info Service API-layer dependencies.

Lazy imports avoid circular dependency with main.py where the engines
and get_db generators are created at import time.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_info_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an Info DB session (commits on success, rolls back on error)."""
    from info_service.main import get_info_db

    async for session in get_info_db():
        yield session


InfoDbSession = Annotated[AsyncSession, Depends(get_info_db_session)]
