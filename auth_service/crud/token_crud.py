"""Token CRUD — persist, query, revoke JWT records."""

import warnings
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.token import Token, TokenType


class TokenCRUD:
    """Data access for Token model."""

    def __init__(self) -> None:
        warnings.warn("TODO: TokenCRUD — implement all methods")

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
        warnings.warn("TODO: implement create")
        raise NotImplementedError("create not implemented")

    async def get_by_value(self, db: AsyncSession, token_value: str) -> Token | None:
        """Find a token by its value."""
        warnings.warn("TODO: implement get_by_value")
        raise NotImplementedError("get_by_value not implemented")

    async def revoke(self, db: AsyncSession, token_id: int) -> None:
        """Mark a token as revoked."""
        warnings.warn("TODO: implement revoke")
        raise NotImplementedError("revoke not implemented")

    async def revoke_all_for_user(self, db: AsyncSession, user_id: str) -> None:
        """Revoke all tokens for a user."""
        warnings.warn("TODO: implement revoke_all_for_user")
        raise NotImplementedError("revoke_all_for_user not implemented")

    async def delete_by_user(self, db: AsyncSession, user_id: str) -> None:
        """Delete all token records for a user."""
        warnings.warn("TODO: implement delete_by_user")
        raise NotImplementedError("delete_by_user not implemented")


token_crud = TokenCRUD()
