"""TrainingProgram request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrainingProgramResponse(BaseModel):
    id: int
    program_code: str
    major_code: str
    grade: str
    version: str = "1.0"
    required_course_ids: str = ""
    snapshot_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TrainingProgramCreateRequest(BaseModel):
    program_code: str = Field(..., min_length=1, max_length=64)
    major_code: str = Field(..., min_length=1, max_length=64)
    grade: str = Field(..., min_length=1, max_length=16)
    version: str = Field(default="1.0", max_length=16)
    required_course_ids: list[int] = Field(default_factory=list)


class TrainingProgramUpdateRequest(BaseModel):
    program_code: str = Field(..., min_length=1, max_length=64)
    major_code: str = Field(..., min_length=1, max_length=64)
    grade: str = Field(..., min_length=1, max_length=16)
    version: str = Field(default="1.0", max_length=16)
    required_course_ids: list[int] = Field(default_factory=list)


class TrainingProgramPatchRequest(BaseModel):
    major_code: Optional[str] = Field(default=None, max_length=64)
    grade: Optional[str] = Field(default=None, max_length=16)
    version: Optional[str] = Field(default=None, max_length=16)
    required_course_ids: Optional[list[int]] = None
