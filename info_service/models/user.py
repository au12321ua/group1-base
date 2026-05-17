"""User main table in Info DB — full user business data."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class UserInfo(SQLModel, table=True):
    """Main user record in Info DB.

    Linked to Auth DB via userId (logical, no FK constraint).
    """

    __tablename__: str = "users_info"

    id: int | None = Field(default=None, primary_key=True)
    user_no: str = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=128, unique=True, index=True)
    role_ids: str = Field(default="", max_length=512)  # comma-separated role IDs
    profile_id: int | None = Field(default=None)
    is_deleted: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
