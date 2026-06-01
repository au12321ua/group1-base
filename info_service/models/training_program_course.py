"""TrainingProgramCourse model — M:N association between training programs and courses."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class TrainingProgramCourse(SQLModel, table=True):
    """M:N association between training programs and required courses."""

    __tablename__: str = "training_program_courses"
    __table_args__ = (
        UniqueConstraint(
            "program_id", "course_id",
            name="uq_program_course",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    program_id: int = Field(foreign_key="training_programs.id", index=True)
    course_id: int = Field(foreign_key="courses.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
