"""Credential model — password hash, failed login tracking, lock state."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Credential(SQLModel, table=True):
    """Authentication credential for a user."""

    __tablename__: str = "credentials"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, unique=True, index=True)
    # 登录冗余字段，唯一性由 users.username 保证；仅加索引加速 lookup
    username: str = Field(max_length=128, index=True)
    password_hash: str = Field(max_length=256)
    password_salt: str = Field(max_length=128)
    failed_login_count: int = Field(default=0)
    locked_until: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
