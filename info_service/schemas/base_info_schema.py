"""BaseInfoItem request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class BaseInfoResponse(BaseModel):
    id: int
    category: str
    item_code: str
    item_name: str
    description: str = ""
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BaseInfoCreateRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=64)
    item_code: str = Field(..., min_length=1, max_length=64)
    item_name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=512)


class BaseInfoUpdateRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=64)
    item_code: str = Field(..., min_length=1, max_length=64)
    item_name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=512)
    is_active: bool = True


class BaseInfoPatchRequest(BaseModel):
    category: str | None = Field(default=None, max_length=64)
    item_code: str | None = Field(default=None, max_length=64)
    item_name: str | None = Field(default=None, max_length=256)
    description: str | None = Field(default=None, max_length=512)
    is_active: bool | None = None
