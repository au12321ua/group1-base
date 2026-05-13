"""CourseOffering request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OfferingResponse(BaseModel):
    id: int
    course_id: int
    term_code: str
    class_no: str
    teacher_ids: str = ""
    capacity: int = 0
    status: str = "ACTIVE"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OfferingCreateRequest(BaseModel):
    course_id: int
    term_code: str = Field(..., min_length=1, max_length=32)
    class_no: str = Field(..., min_length=1, max_length=32)
    teacher_ids: list[str] = Field(default_factory=list)
    capacity: int = Field(default=0, ge=0)


class OfferingUpdateRequest(BaseModel):
    course_id: int
    term_code: str = Field(..., min_length=1, max_length=32)
    class_no: str = Field(..., min_length=1, max_length=32)
    teacher_ids: list[str] = Field(default_factory=list)
    capacity: int = Field(default=0, ge=0)
    status: str = Field(default="ACTIVE")


class OfferingPatchRequest(BaseModel):
    term_code: Optional[str] = Field(default=None, max_length=32)
    class_no: Optional[str] = Field(default=None, max_length=32)
    teacher_ids: Optional[list[str]] = None
    capacity: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = Field(default=None, max_length=32)
