"""Info Service — /audit-logs/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.audit_log_schema import AuditLogQuery, AuditLogResponse
from shared.response import ListResponse, SingleResponse

router = APIRouter(tags=["audit-logs"])


@router.get("/", response_model=ListResponse[AuditLogResponse])
async def search_audit_logs(query: AuditLogQuery = Query()) -> ListResponse[AuditLogResponse]:
    """Search audit logs with filters (requires audit:read permission)."""
    warnings.warn("TODO: implement GET /audit-logs")
    raise NotImplementedError("GET /audit-logs not implemented")


@router.get("/export", response_model=SingleResponse[str])
async def export_audit_logs(
    operator_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> SingleResponse[str]:
    """Export audit logs as CSV (requires audit:read permission)."""
    warnings.warn("TODO: implement GET /audit-logs/export")
    raise NotImplementedError("GET /audit-logs/export not implemented")
