"""Credential model — password hash, failed login tracking, lock state."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Credential(SQLModel, table=True):
    """Authentication credential for a user."""

    __tablename__ = "credentials"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=128)
    password_hash: str = Field(max_length=256)
    password_salt: str = Field(max_length=128)
    failed_login_count: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
