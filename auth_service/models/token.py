"""Token model — persisted JWT records with revocation support."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class TokenType(StrEnum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    SERVICE = "SERVICE"


class Token(SQLModel, table=True):
    """Persisted token record for lifecycle management and revocation."""

    __tablename__: str = "tokens"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, index=True)
    type: TokenType
    # 原型明文存储；生产宜改为 token_hash（见 PR 讨论）
    token_value: str = Field(max_length=512, unique=True, index=True)
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)
