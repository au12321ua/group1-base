"""Info Service — /offerings/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.offering_schema import (
    OfferingCreateRequest,
    OfferingPatchRequest,
    OfferingResponse,
    OfferingUpdateRequest,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["offerings"])


@router.get("/", response_model=ListResponse[OfferingResponse])
async def list_offerings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    course_id: int | None = Query(default=None),
    term_code: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> ListResponse[OfferingResponse]:
    """Get paginated offering list."""
    warnings.warn("TODO: implement GET /offerings")
    raise NotImplementedError("GET /offerings not implemented")


@router.post("/", response_model=SingleResponse[OfferingResponse])
async def create_offering(request: OfferingCreateRequest) -> SingleResponse[OfferingResponse]:
    """Create a new offering."""
    warnings.warn("TODO: implement POST /offerings")
    raise NotImplementedError("POST /offerings not implemented")


@router.get("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def get_offering(offering_id: int) -> SingleResponse[OfferingResponse]:
    """Get offering detail."""
    warnings.warn("TODO: implement GET /offerings/{id}")
    raise NotImplementedError("GET /offerings/{id} not implemented")


@router.put("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def update_offering(offering_id: int, request: OfferingUpdateRequest) -> SingleResponse[OfferingResponse]:
    """Full update offering."""
    warnings.warn("TODO: implement PUT /offerings/{id}")
    raise NotImplementedError("PUT /offerings/{id} not implemented")


@router.patch("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def patch_offering(offering_id: int, request: OfferingPatchRequest) -> SingleResponse[OfferingResponse]:
    """Partial update offering."""
    warnings.warn("TODO: implement PATCH /offerings/{id}")
    raise NotImplementedError("PATCH /offerings/{id} not implemented")


@router.delete("/{offering_id}", response_model=APIResponse[None])
async def delete_offering(offering_id: int) -> APIResponse[None]:
    """Delete offering."""
    warnings.warn("TODO: implement DELETE /offerings/{id}")
    raise NotImplementedError("DELETE /offerings/{id} not implemented")
