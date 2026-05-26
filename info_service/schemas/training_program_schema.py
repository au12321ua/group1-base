"""TrainingProgram request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TrainingProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    program_code: str
    major_code: str
    grade: str
    version: str = "1.0"
    required_course_ids: str = ""
    snapshot_time: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
    major_code: str | None = Field(default=None, max_length=64)
    grade: str | None = Field(default=None, max_length=16)
    version: str | None = Field(default=None, max_length=16)
    required_course_ids: list[int] | None = None
