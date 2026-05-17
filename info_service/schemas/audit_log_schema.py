"""AuditLog request/response schemas."""

from datetime import datetime

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
    created_at: datetime | None = None


class AuditLogQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    operator_user_id: str | None = None
    target_type: str | None = None
    action: str | None = None
    result: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class AuditLogExportResponse(BaseModel):
    download_url: str
    total_count: int
