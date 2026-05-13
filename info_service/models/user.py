"""User main table in Info DB — full user business data."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UserInfo(SQLModel, table=True):
    """Main user record in Info DB.

    Linked to Auth DB via userId (logical, no FK constraint).
    """

    __tablename__ = "users_info"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_no: str = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=128, unique=True, index=True)
    role_ids: str = Field(default="", max_length=512)  # comma-separated role IDs
    profile_id: Optional[int] = Field(default=None, foreign_key="user_profiles.id")
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
