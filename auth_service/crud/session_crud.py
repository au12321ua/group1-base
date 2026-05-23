"""Session CRUD — login session lifecycle management."""

from datetime import UTC, datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.session import AuthenticationSession, SessionStatus


class SessionCRUD:
    """Data access for AuthenticationSession model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        access_token_id: int,
        refresh_token_id: int,
        client_ip: str | None = None,
    ) -> AuthenticationSession:
        """Create a new login session."""
        session = AuthenticationSession(
            user_id=user_id,
            access_token_id=access_token_id,
            refresh_token_id=refresh_token_id,
            client_ip=client_ip,
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)
        return session

    async def get_by_refresh_token_id(
        self, db: AsyncSession, refresh_token_id: int
    ) -> AuthenticationSession | None:
        """Find session linked to a refresh token."""
        result = await db.exec(
            select(AuthenticationSession).where(
                AuthenticationSession.refresh_token_id == refresh_token_id
            )
        )
        return result.first()

    async def end_session(self, db: AsyncSession, session_id: int) -> None:
        """End an ACTIVE session (status=ENDED, set ended_at once)."""
        result = await db.exec(
            select(AuthenticationSession).where(AuthenticationSession.id == session_id)
        )
        session = result.first()
        if session is None or session.status != SessionStatus.ACTIVE:
            return
        session.status = SessionStatus.ENDED
        if session.ended_at is None:
            session.ended_at = datetime.now(UTC)
        db.add(session)
        await db.flush()

    async def expire_session(self, db: AsyncSession, session_id: int) -> None:
        """Mark an ACTIVE session as expired (set ended_at once)."""
        result = await db.exec(
            select(AuthenticationSession).where(AuthenticationSession.id == session_id)
        )
        session = result.first()
        if session is None or session.status != SessionStatus.ACTIVE:
            return
        session.status = SessionStatus.EXPIRED
        if session.ended_at is None:
            session.ended_at = datetime.now(UTC)
        db.add(session)
        await db.flush()

    async def delete_by_user(self, db: AsyncSession, user_id: str) -> None:
        """Delete all sessions for a user (cleanup on physical delete)."""
        result = await db.exec(
            select(AuthenticationSession).where(AuthenticationSession.user_id == user_id)
        )
        for session in result.all():
            await db.delete(session)
        await db.flush()


session_crud = SessionCRUD()
