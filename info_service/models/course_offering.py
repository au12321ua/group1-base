"""CourseOffering model — a specific offering/class of a course."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class CourseOffering(SQLModel, table=True):
    """A specific offering instance of a course (e.g. 2025 Fall, Class A)."""

    __tablename__: str = "course_offerings"

    id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="courses.id", index=True)
    term_code: str = Field(max_length=32, index=True)
    class_no: str = Field(max_length=32)
    teacher_ids: str = Field(default="", max_length=512)  # comma-separated teacher IDs
    capacity: int = Field(default=0)
    status: str = Field(default="ACTIVE", max_length=32)  # ACTIVE / CANCELLED / COMPLETED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
