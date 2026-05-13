"""CourseSchedule request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScheduleResponse(BaseModel):
    id: int
    offering_id: int
    classroom_id: int
    day_of_week: int
    start_period: int
    end_period: int
    week_range: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
    classroom_id: Optional[int] = None
    day_of_week: Optional[int] = Field(default=None, ge=1, le=7)
    start_period: Optional[int] = Field(default=None, ge=1, le=12)
    end_period: Optional[int] = Field(default=None, ge=1, le=12)
    week_range: Optional[str] = None


class TeacherAssignmentResponse(BaseModel):
    id: int
    teacher_id: str
    offering_id: int
    role_type: str = "instructor"
    created_at: Optional[datetime] = None


class TeacherAssignmentCreateRequest(BaseModel):
    teacher_id: str
    role_type: str = "instructor"
