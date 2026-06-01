"""User main table in Info DB — full user business data."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class UserInfo(SQLModel, table=True):
    """Main user record in Info DB.

    Linked to Auth DB via userId (logical, no FK constraint).
    Role information is managed by Auth Service — Info Service receives
    it via X-User-Role header from the Gateway.
    UserProfile provides 1:1 profile data via user_id FK.
    """

    __tablename__: str = "users_info"

    id: int | None = Field(default=None, primary_key=True)
    user_no: str = Field(max_length=64, unique=True, index=True)
    username: str = Field(max_length=128, unique=True, index=True)
    is_deleted: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
