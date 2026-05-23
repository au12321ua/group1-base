"""Course model — core curriculum data."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Course(SQLModel, table=True):
    """Course master data."""

    __tablename__: str = "courses"

    id: int | None = Field(default=None, primary_key=True)
    course_code: str = Field(max_length=64, unique=True, index=True)
    course_name: str = Field(max_length=256)
    credit: int = Field(default=0)
    capacity: int = Field(default=0)
    assessment_method: str = Field(default="", max_length=128)
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
