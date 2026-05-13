"""Authentication session model — login session lifecycle."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"
    EXPIRED = "EXPIRED"


class AuthenticationSession(SQLModel, table=True):
    """Tracks a user login session from login to logout."""

    __tablename__ = "authentication_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    access_token_id: int
    refresh_token_id: int
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    client_ip: Optional[str] = Field(default=None, max_length=45)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
