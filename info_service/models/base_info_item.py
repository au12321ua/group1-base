"""BaseInfoItem model — generic key-value info entries (e.g. departments, titles)."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class BaseInfoItem(SQLModel, table=True):
    """Generic lookup / reference data entry."""

    __tablename__: str = "base_info_items"
    __table_args__ = (
        UniqueConstraint(
            "category", "item_code",
            name="uq_base_info_category_item",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    category: str = Field(max_length=64, index=True)  # e.g. "department", "title"
    item_code: str = Field(max_length=64)
    item_name: str = Field(max_length=256)
    description: str = Field(default="", max_length=512)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
