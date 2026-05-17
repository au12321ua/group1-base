"""RecycleBin request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class RecycleBinItemResponse(BaseModel):
    id: int
    user_no: str
    username: str
    full_name: str = ""
    role_ids: str = ""
    deleted_at: datetime | None = None


class BatchDeleteRequest(BaseModel):
    user_ids: list[int] = Field(..., min_length=1)
