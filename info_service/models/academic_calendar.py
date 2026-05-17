"""AcademicCalendar model — term/semester calendar data."""

from datetime import UTC, date, datetime

from sqlmodel import Field, SQLModel


class AcademicCalendar(SQLModel, table=True):
    """Academic calendar entry (typically one per term)."""

    __tablename__: str = "academic_calendars"

    id: int | None = Field(default=None, primary_key=True)
    term_code: str = Field(max_length=32, unique=True, index=True)
    term_name: str = Field(max_length=128)
    start_date: date
    end_date: date
    version: str = Field(default="1.0", max_length=16)
    snapshot_time: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
