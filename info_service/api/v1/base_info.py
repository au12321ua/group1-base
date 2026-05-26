"""Info Service — /base-info/* endpoints."""

from fastapi import APIRouter, Query

from info_service.api.deps import InfoDbSession
from info_service.schemas.base_info_schema import (
    BaseInfoCreateRequest,
    BaseInfoPatchRequest,
    BaseInfoResponse,
    BaseInfoUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.response import APIResponse, PaginatedData, PaginationMeta, SingleResponse

router = APIRouter(tags=["base-info"])


@router.get("/", response_model=APIResponse[PaginatedData[BaseInfoResponse]])
async def list_base_info(
    db: InfoDbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
) -> APIResponse[PaginatedData[BaseInfoResponse]]:
    """Get paginated base info list, optionally filtered by category."""
    items, total = await course_management_service.list_base_info(
        db, page=page, page_size=page_size, category=category
    )
    return APIResponse(
        data=PaginatedData(
            items=[BaseInfoResponse.model_validate(i) for i in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[BaseInfoResponse])
async def create_base_info(
    request: BaseInfoCreateRequest, db: InfoDbSession
) -> SingleResponse[BaseInfoResponse]:
    """Create a base info entry."""
    item = await course_management_service.create_base_info(db, request)
    return SingleResponse(data=BaseInfoResponse.model_validate(item))


@router.get("/{item_id}", response_model=SingleResponse[BaseInfoResponse])
async def get_base_info(item_id: int, db: InfoDbSession) -> SingleResponse[BaseInfoResponse]:
    """Get base info detail."""
    item = await course_management_service.get_base_info(db, item_id)
    return SingleResponse(data=BaseInfoResponse.model_validate(item))


@router.put("/{item_id}", response_model=SingleResponse[BaseInfoResponse])
async def update_base_info(
    item_id: int, request: BaseInfoUpdateRequest, db: InfoDbSession
) -> SingleResponse[BaseInfoResponse]:
    """Full update base info."""
    item = await course_management_service.update_base_info(db, item_id, request)
    return SingleResponse(data=BaseInfoResponse.model_validate(item))


@router.patch("/{item_id}", response_model=SingleResponse[BaseInfoResponse])
async def patch_base_info(
    item_id: int, request: BaseInfoPatchRequest, db: InfoDbSession
) -> SingleResponse[BaseInfoResponse]:
    """Partial update base info."""
    item = await course_management_service.patch_base_info(db, item_id, request)
    return SingleResponse(data=BaseInfoResponse.model_validate(item))


@router.delete("/{item_id}", response_model=APIResponse[None])
async def delete_base_info(item_id: int, db: InfoDbSession) -> APIResponse[None]:
    """Delete base info entry."""
    await course_management_service.delete_base_info(db, item_id)
    return APIResponse(data=None)
