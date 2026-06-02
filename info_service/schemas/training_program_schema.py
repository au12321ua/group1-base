"""TrainingProgram request/response schemas.

Required courses are stored in the TrainingProgramCourse association table
and exposed as both list[int] (legacy) and list[CourseBrief] (enriched)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseBrief(BaseModel):
    """Minimal course reference for enrichment."""

    id: int
    course_code: str
    course_name: str


class TrainingProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    program_code: str
    major_code: str
    grade: str
    version: str = "1.0"
    required_course_ids: list[int] = Field(default_factory=list)
    required_courses: list[CourseBrief] = Field(default_factory=list)
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
