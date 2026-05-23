"""Authentication session model — login session lifecycle."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class SessionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    EXPIRED = "EXPIRED"


class AuthenticationSession(SQLModel, table=True):
    """Tracks a user login session from login to logout."""

    __tablename__: str = "authentication_sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    access_token_id: int
    refresh_token_id: int
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    client_ip: str | None = Field(default=None, max_length=45)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = Field(default=None)
