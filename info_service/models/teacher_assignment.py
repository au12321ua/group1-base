"""TeacherCourseAssignment model — links teachers to course offerings."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class TeacherCourseAssignment(SQLModel, table=True):
    """Assignment of a teacher to a course offering with a specific role."""

    __tablename__: str = "teacher_course_assignments"

    id: int | None = Field(default=None, primary_key=True)
    teacher_id: str = Field(max_length=64, index=True)  # user_id of teacher
    offering_id: int = Field(foreign_key="course_offerings.id", index=True)
    role_type: str = Field(default="instructor", max_length=32)  # instructor / assistant / lab
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
