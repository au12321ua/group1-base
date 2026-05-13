"""Course-related request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CourseResponse(BaseModel):
    id: int
    course_code: str
    course_name: str
    credit: int = 0
    capacity: int = 0
    assessment_method: str = ""
    is_active: bool = True
    is_deleted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CourseCreateRequest(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=64)
    course_name: str = Field(..., min_length=1, max_length=256)
    credit: int = Field(default=0, ge=0)
    capacity: int = Field(default=0, ge=0)
    assessment_method: str = Field(default="", max_length=128)


class CourseUpdateRequest(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=64)
    course_name: str = Field(..., min_length=1, max_length=256)
    credit: int = Field(default=0, ge=0)
    capacity: int = Field(default=0, ge=0)
    assessment_method: str = Field(default="", max_length=128)
    is_active: bool = True


class CoursePatchRequest(BaseModel):
    course_code: Optional[str] = Field(default=None, max_length=64)
    course_name: Optional[str] = Field(default=None, max_length=256)
    credit: Optional[int] = Field(default=None, ge=0)
    capacity: Optional[int] = Field(default=None, ge=0)
    assessment_method: Optional[str] = Field(default=None, max_length=128)
    is_active: Optional[bool] = None
