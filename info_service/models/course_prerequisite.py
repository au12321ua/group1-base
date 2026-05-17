"""CoursePrerequisite model — prerequisite relationships between courses."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class CoursePrerequisite(SQLModel, table=True):
    """Prerequisite relationship: course A requires course B."""

    __tablename__: str = "course_prerequisites"

    id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="courses.id", index=True)
    prerequisite_course_id: int = Field(foreign_key="courses.id")
    min_grade: str = Field(default="", max_length=16)  # minimum grade in prerequisite
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
