"""Info Service — /audit-logs/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.crud.user_profile_crud import user_profile_crud
from info_service.deps import require_permission
from info_service.schemas.audit_log_schema import AuditLogResponse
from info_service.services.audit_service import audit_service
from shared.response import APIResponse, PaginatedData, PaginationMeta
from shared.security import IdentityContext

router = APIRouter(tags=["audit-logs"])


@router.get("/", response_model=APIResponse[PaginatedData[AuditLogResponse]])
async def search_audit_logs(
    audit_db: AuditDbSession,
    info_db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("audit:read"))],
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
        audit_db,
        operator_user_id=operator_user_id,
        target_type=target_type,
        action=action,
        result=result,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    # Batch-fetch operator names from Info DB
    operator_ids = {item.operator_user_id for item in items if item.operator_user_id}
    name_map = await user_profile_crud.batch_get_display_names(info_db, operator_ids)
    result_items = []
    for a in items:
        resp = AuditLogResponse.model_validate(a)
        resp.operator_name = name_map.get(a.operator_user_id) if a.operator_user_id else None
        result_items.append(resp)
    return APIResponse(
        data=PaginatedData(
            items=result_items,
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.get("/export", response_model=APIResponse[str])
async def export_audit_logs(
    db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("audit:read"))],
    operator_user_id: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    result: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
) -> APIResponse[str]:
    """Export audit logs as CSV."""
    csv_content = await audit_service.export_audit_logs(
        db,
        operator_user_id=operator_user_id,
        target_type=target_type,
        action=action,
        result=result,
        start_date=start_date,
        end_date=end_date,
    )
    return APIResponse(data=csv_content)
