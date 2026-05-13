"""RecycleBin request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecycleBinItemResponse(BaseModel):
    id: int
    user_no: str
    username: str
    full_name: str = ""
    role_ids: str = ""
    deleted_at: Optional[datetime] = None


class BatchDeleteRequest(BaseModel):
    user_ids: list[int] = Field(..., min_length=1)
