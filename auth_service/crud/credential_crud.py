"""Credential CRUD — password hash read/write, failed count, lock state."""

import warnings
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.credential import Credential


class CredentialCRUD:
    """Data access for Credential model."""

    def __init__(self) -> None:
        warnings.warn("TODO: CredentialCRUD — implement all methods")

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> Credential | None:
        """Get credential by user_id."""
        warnings.warn("TODO: implement get_by_user_id")
        result = await db.exec(select(Credential).where(Credential.user_id == user_id))
        return result.first()

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: str,
        username: str,
        password_hash: str,
        password_salt: str,
    ) -> Credential:
        """Create a new credential record."""
        warnings.warn("TODO: implement create")
        raise NotImplementedError("create not implemented")

    async def update_password(
        self, db: AsyncSession, user_id: str, password_hash: str, password_salt: str
    ) -> Credential | None:
        """Update password hash for a user."""
        warnings.warn("TODO: implement update_password")
        raise NotImplementedError("update_password not implemented")

    async def increment_failed_count(self, db: AsyncSession, user_id: str) -> int:
        """Increment failed login count, return new count."""
        warnings.warn("TODO: implement increment_failed_count")
        raise NotImplementedError("increment_failed_count not implemented")

    async def reset_failed_count(self, db: AsyncSession, user_id: str) -> None:
        """Reset failed login count to 0."""
        warnings.warn("TODO: implement reset_failed_count")
        raise NotImplementedError("reset_failed_count not implemented")

    async def lock_account(self, db: AsyncSession, user_id: str, until: datetime) -> None:
        """Set locked_until to the given datetime."""
        warnings.warn("TODO: implement lock_account")
        raise NotImplementedError("lock_account not implemented")

    async def unlock_account(self, db: AsyncSession, user_id: str) -> None:
        """Clear locked_until."""
        warnings.warn("TODO: implement unlock_account")
        raise NotImplementedError("unlock_account not implemented")

    async def delete(self, db: AsyncSession, user_id: str) -> bool:
        """Delete credential record. Returns True if deleted."""
        warnings.warn("TODO: implement delete")
        raise NotImplementedError("delete not implemented")


credential_crud = CredentialCRUD()
