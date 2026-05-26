"""CourseOffering request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OfferingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    term_code: str
    class_no: str
    teacher_ids: str = ""
    capacity: int = 0
    status: str = "ACTIVE"
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
    term_code: str | None = Field(default=None, max_length=32)
    class_no: str | None = Field(default=None, max_length=32)
    teacher_ids: list[str] | None = None
    capacity: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=32)
