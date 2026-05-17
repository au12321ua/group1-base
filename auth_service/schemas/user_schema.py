"""Auth Service user schemas (minimal — identity only)."""

from datetime import datetime

from pydantic import BaseModel


class AuthUserResponse(BaseModel):
    user_id: str
    username: str
    status: str
    created_at: datetime | None = None


class AuthUserCreate(BaseModel):
    user_id: str
    username: str


class AuthUserUpdate(BaseModel):
    username: str | None = None
    status: str | None = None
