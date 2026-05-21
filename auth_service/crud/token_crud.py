"""Token CRUD — persist, query, revoke JWT records."""

from datetime import UTC, datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.token import Token, TokenType


class TokenCRUD:
    """Data access for Token model."""

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        token_type: TokenType,
        token_value: str,
        expires_at: datetime,
    ) -> Token:
        """Persist a newly issued token."""
        token = Token(
            user_id=user_id,
            type=token_type,
            token_value=token_value,
            expires_at=expires_at,
        )
        db.add(token)
        await db.flush()
        await db.refresh(token)
        return token

    async def get_by_value(self, db: AsyncSession, token_value: str) -> Token | None:
        """Find a token by its value."""
        result = await db.exec(select(Token).where(Token.token_value == token_value))
        return result.first()

    async def revoke(self, db: AsyncSession, token_id: int) -> None:
        """Mark a token as revoked."""
        result = await db.exec(select(Token).where(Token.id == token_id))
        token = result.first()
        if token is None or token.revoked_at is not None:
            return
        token.revoked_at = datetime.now(UTC).replace(tzinfo=None)
        db.add(token)
        await db.flush()

    async def revoke_all_for_user(self, db: AsyncSession, user_id: str) -> None:
        """Revoke all non-revoked tokens for a user."""
        result = await db.exec(
            select(Token).where(Token.user_id == user_id, Token.revoked_at.is_(None))
        )
        now = datetime.now(UTC).replace(tzinfo=None)
        for token in result.all():
            token.revoked_at = now
            db.add(token)
        await db.flush()

    async def delete_by_user(self, db: AsyncSession, user_id: str) -> None:
        """Delete all token records for a user."""
        result = await db.exec(select(Token).where(Token.user_id == user_id))
        for token in result.all():
            await db.delete(token)
        await db.flush()


token_crud = TokenCRUD()
