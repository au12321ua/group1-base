"""Credential CRUD — password hash read/write, failed count, lock state."""

from datetime import UTC, datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.models.credential import Credential


class CredentialCRUD:
    """Data access for Credential model."""

    async def get_by_user_id(self, db: AsyncSession, user_id: str) -> Credential | None:
        """Get credential by user_id."""
        result = await db.exec(select(Credential).where(Credential.user_id == user_id))
        return result.first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Credential | None:
        """Get credential by username (login lookup)."""
        result = await db.exec(select(Credential).where(Credential.username == username))
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
        credential = Credential(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            password_salt=password_salt,
        )
        db.add(credential)
        await db.flush()
        await db.refresh(credential)
        return credential

    async def update_password(
        self, db: AsyncSession, user_id: str, password_hash: str, password_salt: str
    ) -> Credential | None:
        """Update password hash for a user."""
        credential = await self.get_by_user_id(db, user_id)
        if credential is None:
            return None
        credential.password_hash = password_hash
        credential.password_salt = password_salt
        credential.updated_at = datetime.now(UTC).replace(tzinfo=None)
        db.add(credential)
        await db.flush()
        await db.refresh(credential)
        return credential

    async def increment_failed_count(self, db: AsyncSession, user_id: str) -> int:
        """Increment failed login count, return new count."""
        credential = await self.get_by_user_id(db, user_id)
        if credential is None:
            return 0
        credential.failed_login_count += 1
        credential.updated_at = datetime.now(UTC).replace(tzinfo=None)
        db.add(credential)
        await db.flush()
        return credential.failed_login_count

    async def reset_failed_count(self, db: AsyncSession, user_id: str) -> None:
        """Reset failed login count to 0."""
        credential = await self.get_by_user_id(db, user_id)
        if credential is None:
            return
        credential.failed_login_count = 0
        credential.updated_at = datetime.now(UTC).replace(tzinfo=None)
        db.add(credential)
        await db.flush()

    async def lock_account(self, db: AsyncSession, user_id: str, until: datetime) -> None:
        """Set locked_until to the given datetime."""
        credential = await self.get_by_user_id(db, user_id)
        if credential is None:
            return
        credential.locked_until = until
        credential.updated_at = datetime.now(UTC).replace(tzinfo=None)
        db.add(credential)
        await db.flush()

    async def unlock_account(self, db: AsyncSession, user_id: str) -> None:
        """Clear locked_until."""
        credential = await self.get_by_user_id(db, user_id)
        if credential is None:
            return
        credential.locked_until = None
        credential.updated_at = datetime.now(UTC).replace(tzinfo=None)
        db.add(credential)
        await db.flush()

    async def delete(self, db: AsyncSession, user_id: str) -> bool:
        """Delete credential record. Returns True if deleted."""
        credential = await self.get_by_user_id(db, user_id)
        if credential is None:
            return False
        await db.delete(credential)
        await db.flush()
        return True


credential_crud = CredentialCRUD()
