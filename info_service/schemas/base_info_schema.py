"""BaseInfoItem request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseInfoResponse(BaseModel):
    id: int
    category: str
    item_code: str
    item_name: str
    description: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
    category: Optional[str] = Field(default=None, max_length=64)
    item_code: Optional[str] = Field(default=None, max_length=64)
    item_name: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=512)
    is_active: Optional[bool] = None
