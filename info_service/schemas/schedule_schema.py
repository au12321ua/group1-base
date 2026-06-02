"""CourseSchedule request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    offering_id: int
    classroom_id: int
    course_name: str | None = None
    offering_term_code: str | None = None
    classroom_name: str | None = None
    day_of_week: int
    start_period: int
    end_period: int
    week_range: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ScheduleCreateRequest(BaseModel):
    offering_id: int
    classroom_id: int
    day_of_week: int = Field(..., ge=1, le=7)
    start_period: int = Field(..., ge=1, le=12)
    end_period: int = Field(..., ge=1, le=12)
    week_range: str = Field(default="")


class ScheduleUpdateRequest(BaseModel):
    offering_id: int
    classroom_id: int
    day_of_week: int = Field(..., ge=1, le=7)
    start_period: int = Field(..., ge=1, le=12)
    end_period: int = Field(..., ge=1, le=12)
    week_range: str = Field(default="")


class SchedulePatchRequest(BaseModel):
    offering_id: int | None = None
    classroom_id: int | None = None
    day_of_week: int | None = Field(default=None, ge=1, le=7)
    start_period: int | None = Field(default=None, ge=1, le=12)
    end_period: int | None = Field(default=None, ge=1, le=12)
    week_range: str | None = None


class TeacherAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: str
    teacher_name: str | None = None
    offering_id: int
    role_type: str = "instructor"
    created_at: datetime | None = None


class TeacherAssignmentCreateRequest(BaseModel):
    teacher_id: str
    role_type: str = "instructor"
