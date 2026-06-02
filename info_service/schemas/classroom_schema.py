"""Classroom request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClassroomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_no: str
    building: str = ""
    capacity: int = 0
    type: str = "standard"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ClassroomCreateRequest(BaseModel):
    room_no: str = Field(..., min_length=1, max_length=64)
    building: str = Field(default="", max_length=128)
    capacity: int = Field(default=0, ge=0)
    type: str = Field(default="standard", max_length=64)


class ClassroomUpdateRequest(BaseModel):
    room_no: str = Field(..., min_length=1, max_length=64)
    building: str = Field(default="", max_length=128)
    capacity: int = Field(default=0, ge=0)
    type: str = Field(default="standard", max_length=64)


class ClassroomPatchRequest(BaseModel):
    room_no: str | None = Field(default=None, max_length=64)
    building: str | None = Field(default=None, max_length=128)
    capacity: int | None = Field(default=None, ge=0)
    type: str | None = Field(default=None, max_length=64)
