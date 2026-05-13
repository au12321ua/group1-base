"""User-related request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfileSchema(BaseModel):
    """User profile nested in user responses."""
    full_name: str = ""
    gender: str = ""
    email: str = ""
    phone: str = ""
    status: str = "ACTIVE"
    avatar_file_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    user_no: str
    username: str
    role_ids: str = ""
    is_deleted: bool = False
    profile: Optional[UserProfileSchema] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreateRequest(BaseModel):
    user_no: str = Field(..., min_length=1, max_length=64)
    username: str = Field(..., min_length=1, max_length=128)
    role_ids: list[int] = Field(default_factory=list)
    full_name: str = Field(default="", max_length=128)
    gender: str = Field(default="", max_length=16)
    email: str = Field(default="", max_length=256)
    phone: str = Field(default="", max_length=32)


class UserUpdateRequest(BaseModel):
    """Full update — all fields required."""
    user_no: str = Field(..., min_length=1, max_length=64)
    username: str = Field(..., min_length=1, max_length=128)
    role_ids: list[int] = Field(default_factory=list)
    full_name: str = Field(default="", max_length=128)
    gender: str = Field(default="", max_length=16)
    email: str = Field(default="", max_length=256)
    phone: str = Field(default="", max_length=32)
    status: str = Field(default="ACTIVE", max_length=32)


class UserPatchRequest(BaseModel):
    """Partial update — all fields optional."""
    user_no: Optional[str] = Field(default=None, max_length=64)
    username: Optional[str] = Field(default=None, max_length=128)
    role_ids: Optional[list[int]] = None
    full_name: Optional[str] = Field(default=None, max_length=128)
    gender: Optional[str] = Field(default=None, max_length=16)
    email: Optional[str] = Field(default=None, max_length=256)
    phone: Optional[str] = Field(default=None, max_length=32)
    status: Optional[str] = Field(default=None, max_length=32)


class UserImportResult(BaseModel):
    total: int
    success_count: int
    failed_count: int
    errors: list[dict[str, str]] = Field(default_factory=list)


class UserListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")
    keyword: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
