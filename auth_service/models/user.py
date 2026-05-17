"""Minimal user model for Auth DB — only authentication-essential fields."""

from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class User(SQLModel, table=True):
    """Minimal user record in Auth DB.

    Linked to Info DB via userId — no FK constraint across databases.
    """

    __tablename__: str = "users"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=128, unique=True, index=True)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
