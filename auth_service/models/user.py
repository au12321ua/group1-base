"""Minimal user model for Auth DB — only authentication-essential fields."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class User(SQLModel, table=True):
    """Minimal user record in Auth DB.

    Linked to Info DB via userId — no FK constraint across databases.
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=128, unique=True, index=True)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
