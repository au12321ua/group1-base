"""Info Service — /recycle-bin/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.recycle_bin_schema import (
    BatchDeleteRequest,
    RecycleBinItemResponse,
)
from shared.response import APIResponse, ListResponse

router = APIRouter(tags=["recycle-bin"])


@router.get("/", response_model=ListResponse[RecycleBinItemResponse])
async def list_deleted_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
) -> ListResponse[RecycleBinItemResponse]:
    """List soft-deleted users in recycle bin."""
    warnings.warn("TODO: implement GET /recycle-bin")
    raise NotImplementedError("GET /recycle-bin not implemented")


@router.post("/{user_id}/restore", response_model=APIResponse[None])
async def restore_user(user_id: int) -> APIResponse[None]:
    """Restore a user from recycle bin (cross-service enable Auth account)."""
    warnings.warn("TODO: implement POST /recycle-bin/{id}/restore")
    raise NotImplementedError("POST /recycle-bin/{id}/restore not implemented")


@router.delete("/{user_id}", response_model=APIResponse[None])
async def physical_delete_user(user_id: int) -> APIResponse[None]:
    """Permanently delete user (requires confirmation)."""
    warnings.warn("TODO: implement DELETE /recycle-bin/{id}")
    raise NotImplementedError("DELETE /recycle-bin/{id} not implemented")


@router.post("/batch-delete", response_model=APIResponse[None])
async def batch_physical_delete(request: BatchDeleteRequest) -> APIResponse[None]:
    """Batch permanent delete users."""
    warnings.warn("TODO: implement POST /recycle-bin/batch-delete")
    raise NotImplementedError("POST /recycle-bin/batch-delete not implemented")
