"""Info Service — /base-info/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.base_info_schema import (
    BaseInfoCreateRequest,
    BaseInfoPatchRequest,
    BaseInfoResponse,
    BaseInfoUpdateRequest,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["base-info"])


@router.get("/", response_model=ListResponse[BaseInfoResponse])
async def list_base_info(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
) -> ListResponse[BaseInfoResponse]:
    """Get paginated base info list, optionally filtered by category."""
    warnings.warn("TODO: implement GET /base-info")
    raise NotImplementedError("GET /base-info not implemented")


@router.post("/", response_model=SingleResponse[BaseInfoResponse])
async def create_base_info(request: BaseInfoCreateRequest) -> SingleResponse[BaseInfoResponse]:
    """Create a base info entry."""
    warnings.warn("TODO: implement POST /base-info")
    raise NotImplementedError("POST /base-info not implemented")


@router.get("/{item_id}", response_model=SingleResponse[BaseInfoResponse])
async def get_base_info(item_id: int) -> SingleResponse[BaseInfoResponse]:
    """Get base info detail."""
    warnings.warn("TODO: implement GET /base-info/{id}")
    raise NotImplementedError("GET /base-info/{id} not implemented")


@router.put("/{item_id}", response_model=SingleResponse[BaseInfoResponse])
async def update_base_info(
    item_id: int, request: BaseInfoUpdateRequest
) -> SingleResponse[BaseInfoResponse]:
    """Full update base info."""
    warnings.warn("TODO: implement PUT /base-info/{id}")
    raise NotImplementedError("PUT /base-info/{id} not implemented")


@router.patch("/{item_id}", response_model=SingleResponse[BaseInfoResponse])
async def patch_base_info(
    item_id: int, request: BaseInfoPatchRequest
) -> SingleResponse[BaseInfoResponse]:
    """Partial update base info."""
    warnings.warn("TODO: implement PATCH /base-info/{id}")
    raise NotImplementedError("PATCH /base-info/{id} not implemented")


@router.delete("/{item_id}", response_model=APIResponse[None])
async def delete_base_info(item_id: int) -> APIResponse[None]:
    """Delete base info entry."""
    warnings.warn("TODO: implement DELETE /base-info/{id}")
    raise NotImplementedError("DELETE /base-info/{id} not implemented")
