"""Info Service — /calendars/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.audit import AuditContext
from info_service.deps import require_admin, require_permission
from info_service.schemas.calendar_schema import (
    CalendarCreateRequest,
    CalendarPatchRequest,
    CalendarResponse,
    CalendarUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import AppError, ResourceNotFoundError
from shared.response import APIResponse, PaginatedData, PaginationMeta
from shared.security import IdentityContext

router = APIRouter(tags=["calendars"])


@router.get("/", response_model=APIResponse[PaginatedData[CalendarResponse]])
async def list_calendars(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:read"))],
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


@router.post("/", status_code=201, response_model=APIResponse[CalendarResponse])
async def create_calendar(
    request: CalendarCreateRequest,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:create"))],
) -> APIResponse[CalendarResponse]:
    """Create a calendar entry."""
    audit = AuditContext(audit_db, current_user, "calendar", action="calendar_created")
    try:
        cal = await course_management_service.create_calendar(db, request)
        await audit.log_success(target_id=str(cal.id))
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.get("/by-term", response_model=APIResponse[CalendarResponse])
async def get_calendar_by_term(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:read"))],
    term_code: str = Query(...),
) -> APIResponse[CalendarResponse]:
    """Get calendar by term code."""
    cal = await course_management_service.get_calendar_by_term(db, term_code)
    if cal is None:
        raise ResourceNotFoundError("Calendar", term_code)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.get("/{calendar_id}", response_model=APIResponse[CalendarResponse])
async def get_calendar(
    calendar_id: int,
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:read"))],
) -> APIResponse[CalendarResponse]:
    """Get calendar detail."""
    cal = await course_management_service.get_calendar(db, calendar_id)
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.put("/{calendar_id}", response_model=APIResponse[CalendarResponse])
async def update_calendar(
    calendar_id: int,
    request: CalendarUpdateRequest,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:update"))],
    _admin: None = Depends(require_admin),
) -> APIResponse[CalendarResponse]:
    """Full update calendar (admin only)."""
    audit = AuditContext(audit_db, current_user, "calendar",
                         target_id=str(calendar_id), action="calendar_updated")
    try:
        cal = await course_management_service.update_calendar(db, calendar_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.patch("/{calendar_id}", response_model=APIResponse[CalendarResponse])
async def patch_calendar(
    calendar_id: int,
    request: CalendarPatchRequest,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:update"))],
    _admin: None = Depends(require_admin),
) -> APIResponse[CalendarResponse]:
    """Partial update calendar (admin only)."""
    audit = AuditContext(audit_db, current_user, "calendar",
                         target_id=str(calendar_id), action="calendar_updated")
    try:
        cal = await course_management_service.patch_calendar(db, calendar_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=CalendarResponse.model_validate(cal))


@router.delete("/{calendar_id}", response_model=APIResponse[None])
async def delete_calendar(
    calendar_id: int,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("calendar:delete"))],
    _admin: None = Depends(require_admin),
) -> APIResponse[None]:
    """Delete calendar (admin only)."""
    audit = AuditContext(audit_db, current_user, "calendar",
                         target_id=str(calendar_id), action="calendar_deleted")
    try:
        await course_management_service.delete_calendar(db, calendar_id)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)
