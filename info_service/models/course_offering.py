"""CourseOffering model — a specific offering/class of a course."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class CourseOffering(SQLModel, table=True):
    """A specific offering instance of a course (e.g. 2025 Fall, Class A).

    Teachers are linked via TeacherCourseAssignment, not stored inline.
    """

    __tablename__: str = "course_offerings"
    __table_args__ = (
        UniqueConstraint(
            "course_id", "term_code", "class_no",
            name="uq_offering_course_term_class",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="courses.id", index=True)
    term_code: str = Field(max_length=32, index=True)
    class_no: str = Field(max_length=32)
    capacity: int = Field(default=0)
    status: str = Field(default="ACTIVE", max_length=32)  # ACTIVE / CANCELLED / COMPLETED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
