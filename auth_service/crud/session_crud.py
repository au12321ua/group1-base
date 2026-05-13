"""Session CRUD — login session lifecycle management."""

import warnings
from datetime import datetime
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.session import AuthenticationSession, SessionStatus


class SessionCRUD:
    """Data access for AuthenticationSession model."""

    def __init__(self) -> None:
        warnings.warn("TODO: SessionCRUD — implement all methods")

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        access_token_id: int,
        refresh_token_id: int,
        client_ip: Optional[str] = None,
    ) -> AuthenticationSession:
        """Create a new login session."""
        warnings.warn("TODO: implement create")
        raise NotImplementedError("create not implemented")

    async def end_session(self, db: AsyncSession, session_id: int) -> None:
        """End a session (status=ENDED, set ended_at)."""
        warnings.warn("TODO: implement end_session")
        raise NotImplementedError("end_session not implemented")

    async def expire_session(self, db: AsyncSession, session_id: int) -> None:
        """Mark a session as expired."""
        warnings.warn("TODO: implement expire_session")
        raise NotImplementedError("expire_session not implemented")

    async def delete_by_user(self, db: AsyncSession, user_id: str) -> None:
        """Delete all sessions for a user (cleanup on physical delete)."""
        warnings.warn("TODO: implement delete_by_user")
        raise NotImplementedError("delete_by_user not implemented")


session_crud = SessionCRUD()
