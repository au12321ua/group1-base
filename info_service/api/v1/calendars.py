"""Info Service — /calendars/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.calendar_schema import (
    CalendarCreateRequest,
    CalendarPatchRequest,
    CalendarResponse,
    CalendarUpdateRequest,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["calendars"])


@router.get("/", response_model=ListResponse[CalendarResponse])
async def list_calendars(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ListResponse[CalendarResponse]:
    """Get paginated calendar list."""
    warnings.warn("TODO: implement GET /calendars")
    raise NotImplementedError("GET /calendars not implemented")


@router.post("/", response_model=SingleResponse[CalendarResponse])
async def create_calendar(request: CalendarCreateRequest) -> SingleResponse[CalendarResponse]:
    """Create a calendar entry."""
    warnings.warn("TODO: implement POST /calendars")
    raise NotImplementedError("POST /calendars not implemented")


@router.get("/by-term", response_model=SingleResponse[CalendarResponse])
async def get_calendar_by_term(term_code: str = Query(...)) -> SingleResponse[CalendarResponse]:
    """Get calendar by term code."""
    warnings.warn("TODO: implement GET /calendars/by-term")
    raise NotImplementedError("GET /calendars/by-term not implemented")


@router.get("/{calendar_id}", response_model=SingleResponse[CalendarResponse])
async def get_calendar(calendar_id: int) -> SingleResponse[CalendarResponse]:
    """Get calendar detail."""
    warnings.warn("TODO: implement GET /calendars/{id}")
    raise NotImplementedError("GET /calendars/{id} not implemented")


@router.put("/{calendar_id}", response_model=SingleResponse[CalendarResponse])
async def update_calendar(
    calendar_id: int, request: CalendarUpdateRequest
) -> SingleResponse[CalendarResponse]:
    """Full update calendar."""
    warnings.warn("TODO: implement PUT /calendars/{id}")
    raise NotImplementedError("PUT /calendars/{id} not implemented")


@router.patch("/{calendar_id}", response_model=SingleResponse[CalendarResponse])
async def patch_calendar(
    calendar_id: int, request: CalendarPatchRequest
) -> SingleResponse[CalendarResponse]:
    """Partial update calendar."""
    warnings.warn("TODO: implement PATCH /calendars/{id}")
    raise NotImplementedError("PATCH /calendars/{id} not implemented")


@router.delete("/{calendar_id}", response_model=APIResponse[None])
async def delete_calendar(calendar_id: int) -> APIResponse[None]:
    """Delete calendar."""
    warnings.warn("TODO: implement DELETE /calendars/{id}")
    raise NotImplementedError("DELETE /calendars/{id} not implemented")
