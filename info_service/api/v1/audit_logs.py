"""Info Service — /audit-logs/* endpoints."""

from fastapi import APIRouter, Query

from info_service.api.deps import AuditDbSession
from info_service.schemas.audit_log_schema import AuditLogResponse
from info_service.services.audit_service import audit_service
from shared.response import APIResponse, PaginatedData, PaginationMeta

router = APIRouter(tags=["audit-logs"])


@router.get("/", response_model=APIResponse[PaginatedData[AuditLogResponse]])
async def search_audit_logs(
    db: AuditDbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    operator_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    result: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> APIResponse[PaginatedData[AuditLogResponse]]:
    """Search audit logs with filters."""
    items, total = await audit_service.search_audit_logs(
        db,
        operator_user_id=operator_user_id,
        target_type=target_type,
        action=action,
        result=result,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return APIResponse(
        data=PaginatedData(
            items=[AuditLogResponse.model_validate(a) for a in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.get("/export", response_model=APIResponse[str])
async def export_audit_logs(
    db: AuditDbSession,
    operator_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> APIResponse[str]:
    """Export audit logs as CSV."""
    csv_content = await audit_service.export_audit_logs(
        db,
        operator_user_id=operator_user_id,
        target_type=target_type,
        action=action,
        start_date=start_date,
        end_date=end_date,
    )
    return APIResponse(data=csv_content)
