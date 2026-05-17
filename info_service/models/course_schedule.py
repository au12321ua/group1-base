"""CourseSchedule model — time/room scheduling for an offering."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class CourseSchedule(SQLModel, table=True):
    """A scheduled session of a course offering."""

    __tablename__: str = "course_schedules"

    id: int | None = Field(default=None, primary_key=True)
    offering_id: int = Field(foreign_key="course_offerings.id", index=True)
    classroom_id: int = Field(foreign_key="classrooms.id")
    day_of_week: int = Field(ge=1, le=7)  # 1=Mon, 7=Sun
    start_period: int = Field(ge=1, le=12)
    end_period: int = Field(ge=1, le=12)
    week_range: str = Field(default="", max_length=64)  # e.g. "1-16" or "1,3,5,7-16"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
