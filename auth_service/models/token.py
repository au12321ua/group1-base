"""Token model — persisted JWT records with revocation support."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TokenType(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    SERVICE = "SERVICE"


class Token(SQLModel, table=True):
    """Persisted token record for lifecycle management and revocation."""

    __tablename__ = "tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    type: TokenType
    token_value: str = Field(max_length=512)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    revoked_at: Optional[datetime] = Field(default=None)
