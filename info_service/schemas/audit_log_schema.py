"""AuditLog request/response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: int
    operator_user_id: str
    operator_role: str
    target_type: str
    target_id: str = ""
    action: str
    result: str
    reason: str = ""
    request_id: str = ""
    created_at: Optional[datetime] = None


class AuditLogQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    operator_user_id: Optional[str] = None
    target_type: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditLogExportResponse(BaseModel):
    download_url: str
    total_count: int
