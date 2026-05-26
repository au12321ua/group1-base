"""Info Service — /calendars/* endpoints."""

from fastapi import APIRouter, Query

from info_service.api.deps import InfoDbSession
from info_service.schemas.calendar_schema import (
    CalendarCreateRequest,
    CalendarPatchRequest,
    CalendarResponse,
    CalendarUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import ResourceNotFoundError
from shared.response import APIResponse, PaginatedData, PaginationMeta

router = APIRouter(tags=["calendars"])


@router.get("/", response_model=APIResponse[PaginatedData[CalendarResponse]])
async def list_calendars(
    db: InfoDbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> APIResponse[PaginatedData[CalendarResponse]]:
    """Get paginated calendar list."""
    items, total = await course_management_service.list_calendars(db, page, page_size)
    return APIResponse(
        data=PaginatedData(
            items=[CalendarResponse.model_validate(c) for c in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=APIResponse[CalendarResponse])
async def create_calendar(
    request: CalendarCreateRequest, db: InfoDbSession
) -> APIResponse[CalendarResponse]:
    """Create a calendar entry."""
    cal = await course_management_service.create_calendar(db, request)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.get("/by-term", response_model=APIResponse[CalendarResponse])
async def get_calendar_by_term(
    db: InfoDbSession,
    term_code: str = Query(...),
) -> APIResponse[CalendarResponse]:
    """Get calendar by term code."""
    cal = await course_management_service.get_calendar_by_term(db, term_code)
    if cal is None:
        raise ResourceNotFoundError("Calendar", term_code)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.get("/{calendar_id}", response_model=APIResponse[CalendarResponse])
async def get_calendar(calendar_id: int, db: InfoDbSession) -> APIResponse[CalendarResponse]:
    """Get calendar detail."""
    cal = await course_management_service.get_calendar(db, calendar_id)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.put("/{calendar_id}", response_model=APIResponse[CalendarResponse])
async def update_calendar(
    calendar_id: int, request: CalendarUpdateRequest, db: InfoDbSession
) -> APIResponse[CalendarResponse]:
    """Full update calendar."""
    cal = await course_management_service.update_calendar(db, calendar_id, request)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.patch("/{calendar_id}", response_model=APIResponse[CalendarResponse])
async def patch_calendar(
    calendar_id: int, request: CalendarPatchRequest, db: InfoDbSession
) -> APIResponse[CalendarResponse]:
    """Partial update calendar."""
    cal = await course_management_service.patch_calendar(db, calendar_id, request)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.delete("/{calendar_id}", response_model=APIResponse[None])
async def delete_calendar(calendar_id: int, db: InfoDbSession) -> APIResponse[None]:
    """Delete calendar."""
    await course_management_service.delete_calendar(db, calendar_id)
    return APIResponse(data=None)
