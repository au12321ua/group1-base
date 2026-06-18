"""User profile model — detailed personal information."""

from datetime import UTC, datetime

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
    # ACTIVE / DISABLED（软删除时设为 DISABLED
    status: str = Field(default="ACTIVE", max_length=32)
    avatar_file_id: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
