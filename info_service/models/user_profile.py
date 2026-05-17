"""User profile model — detailed personal information."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class UserProfile(SQLModel, table=True):
    """Detailed user profile."""

    __tablename__: str = "user_profiles"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users_info.id", unique=True, index=True)
    full_name: str = Field(default="", max_length=128)
    gender: str = Field(default="", max_length=16)
    email: str = Field(default="", max_length=256)
    phone: str = Field(default="", max_length=32)
    status: str = Field(default="ACTIVE", max_length=32)  # ACTIVE / DISABLED / DELETED
    avatar_file_id: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
