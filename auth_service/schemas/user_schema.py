"""Auth Service user schemas (minimal — identity only)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuthUserResponse(BaseModel):
    user_id: str
    username: str
    status: str
    created_at: Optional[datetime] = None


class AuthUserCreate(BaseModel):
    user_id: str
    username: str


class AuthUserUpdate(BaseModel):
    username: Optional[str] = None
    status: Optional[str] = None
