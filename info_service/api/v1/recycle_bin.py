"""Info Service — /recycle-bin/* endpoints."""

from fastapi import APIRouter, Query

from info_service.api.deps import InfoDbSession
from info_service.schemas.recycle_bin_schema import (
    BatchDeleteRequest,
    RecycleBinItemResponse,
)
from info_service.services.recycle_bin_service import recycle_bin_service
from shared.response import APIResponse, PaginatedData, PaginationMeta

router = APIRouter(tags=["recycle-bin"])


@router.get("/", response_model=APIResponse[PaginatedData[RecycleBinItemResponse]])
async def list_deleted_users(
    db: InfoDbSession,
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
async def restore_user(user_id: int, db: InfoDbSession) -> APIResponse[None]:
    """Restore a user from recycle bin (cross-service enable Auth account)."""
    await recycle_bin_service.restore_user(db, user_id)
    return APIResponse(data=None)


@router.delete("/{user_id}", response_model=APIResponse[None])
async def physical_delete_user(user_id: int, db: InfoDbSession) -> APIResponse[None]:
    """Permanently delete user (requires confirmation)."""
    await recycle_bin_service.physical_delete_user(db, user_id)
    return APIResponse(data=None)


@router.post("/batch-delete", response_model=APIResponse[None])
async def batch_physical_delete(
    request: BatchDeleteRequest, db: InfoDbSession
) -> APIResponse[None]:
    """Batch permanent delete users."""
    await recycle_bin_service.batch_physical_delete(db, request.user_ids)
    return APIResponse(data=None)
