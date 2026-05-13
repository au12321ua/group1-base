"""CoursePrerequisite model — prerequisite relationships between courses."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CoursePrerequisite(SQLModel, table=True):
    """Prerequisite relationship: course A requires course B."""

    __tablename__ = "course_prerequisites"

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="courses.id", index=True)
    prerequisite_course_id: int = Field(foreign_key="courses.id")
    min_grade: str = Field(default="", max_length=16)  # minimum grade in prerequisite
    created_at: datetime = Field(default_factory=datetime.utcnow)
