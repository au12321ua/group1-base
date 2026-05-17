"""AcademicCalendar request/response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class CalendarResponse(BaseModel):
    id: int
    term_code: str
    term_name: str
    start_date: date
    end_date: date
    version: str = "1.0"
    snapshot_time: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CalendarCreateRequest(BaseModel):
    term_code: str = Field(..., min_length=1, max_length=32)
    term_name: str = Field(..., min_length=1, max_length=128)
    start_date: date
    end_date: date
    version: str = Field(default="1.0", max_length=16)


class CalendarUpdateRequest(BaseModel):
    term_code: str = Field(..., min_length=1, max_length=32)
    term_name: str = Field(..., min_length=1, max_length=128)
    start_date: date
    end_date: date
    version: str = Field(default="1.0", max_length=16)


class CalendarPatchRequest(BaseModel):
    term_name: str | None = Field(default=None, max_length=128)
    start_date: date | None = None
    end_date: date | None = None
    version: str | None = Field(default=None, max_length=16)
