"""Info Service — /recycle-bin/* endpoints."""

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.deps import require_permission
from info_service.schemas.recycle_bin_schema import (
    BatchDeleteRequest,
    RecycleBinItemResponse,
)
from info_service.services.audit_service import audit_service
from info_service.services.recycle_bin_service import recycle_bin_service
from shared.response import APIResponse, PaginatedData, PaginationMeta
from shared.security import IdentityContext

router = APIRouter(tags=["recycle-bin"])


@router.get("/", response_model=APIResponse[PaginatedData[RecycleBinItemResponse]])
async def list_deleted_users(
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("recycle:read")),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
) -> APIResponse[PaginatedData[RecycleBinItemResponse]]:
    """List soft-deleted users in recycle bin."""
    items, total = await recycle_bin_service.list_deleted_users(
        db, page=page, page_size=page_size, keyword=keyword
    )
    return APIResponse(
        data=PaginatedData(
            items=[RecycleBinItemResponse.model_validate(u) for u in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/{user_id}/restore", response_model=APIResponse[None])
async def restore_user(
    user_id: int,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: IdentityContext = Depends(require_permission("recycle:restore")),
) -> APIResponse[None]:
    """Restore a user from recycle bin (cross-service enable Auth account)."""
    await recycle_bin_service.restore_user(db, user_id)
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user.user_id,
        operator_role=current_user.role,
        target_type="user",
        target_id=str(user_id),
        action="user_restored",
        result="success",
        request_id=current_user.request_id,
    )
    return APIResponse(data=None)


@router.delete("/{user_id}", response_model=APIResponse[None])
async def physical_delete_user(
    user_id: int,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: IdentityContext = Depends(require_permission("recycle:delete")),
) -> APIResponse[None]:
    """Permanently delete user (requires confirmation)."""
    await recycle_bin_service.physical_delete_user(db, user_id)
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user.user_id,
        operator_role=current_user.role,
        target_type="user",
        target_id=str(user_id),
        action="user_deleted_permanent",
        result="success",
        request_id=current_user.request_id,
    )
    return APIResponse(data=None)


@router.post("/batch-delete", response_model=APIResponse[None])
async def batch_physical_delete(
    request: BatchDeleteRequest,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: IdentityContext = Depends(require_permission("recycle:delete")),
) -> APIResponse[None]:
    """Batch permanent delete users."""
    await recycle_bin_service.batch_physical_delete(db, request.user_ids)
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user.user_id,
        operator_role=current_user.role,
        target_type="user",
        action="user_batch_deleted",
        result="success",
        reason=f"deleted {len(request.user_ids)} users",
        request_id=current_user.request_id,
    )
    return APIResponse(data=None)
