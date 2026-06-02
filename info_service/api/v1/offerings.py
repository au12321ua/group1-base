"""Info Service — /offerings/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.audit import AuditContext
from info_service.core.security import check_resource_access
from info_service.crud.course_crud import course_crud
from info_service.crud.teacher_assignment_crud import teacher_assignment_crud
from info_service.deps import require_permission
from info_service.models.course_offering import CourseOffering
from info_service.schemas.offering_schema import (
    OfferingCreateRequest,
    OfferingPatchRequest,
    OfferingResponse,
    OfferingUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import AppError, AuthorizationError
from shared.response import (
    APIResponse,
    ListResponse,
    PaginatedData,
    PaginationMeta,
    SingleResponse,
)
from shared.security import IdentityContext

router = APIRouter(tags=["offerings"])


async def _check_offering_access(
    current_user: IdentityContext, db, offering_id: int,
) -> CourseOffering:
    """Verify the current user can modify the offering, returning it for reuse."""
    offering = await course_management_service.get_offering(db, offering_id)
    # Teachers are stored in TeacherCourseAssignment, not inline on the offering
    assignments = await teacher_assignment_crud.get_by_offering(db, offering_id)
    teacher_ids = [a.teacher_id for a in assignments]
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_teacher_ids=teacher_ids,
    ):
        raise AuthorizationError(
            "Access denied: only assigned teachers or administrators can modify this offering"
        )
    return offering


@router.get("/", response_model=ListResponse[OfferingResponse])
async def list_offerings(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    course_id: int | None = Query(default=None),
    term_code: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> ListResponse[OfferingResponse]:
    """Get paginated offering list."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_offerings(
        db,
        skip=skip,
        limit=page_size,
        course_id=course_id,
        term_code=term_code,
        status=status,
    )
    # Enrich with course info
    course_ids = {item.course_id for item in items}
    course_map = await course_crud.batch_get_by_ids(db, course_ids)
    result = [
        await _enrich_offering(db, item, course_map=course_map)
        for item in items
    ]
    return ListResponse(
        data=PaginatedData(
            items=result,
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


async def _enrich_offering(
    db, offering: CourseOffering, course_map: dict | None = None,
) -> OfferingResponse:
    """Enrich a single offering response with course info.

    Accepts an optional pre-fetched *course_map* so list endpoints can
    pass the result of a single batch query.
    """
    resp = OfferingResponse.model_validate(offering)
    if course_map is None:
        course_map = await course_crud.batch_get_by_ids(db, {offering.course_id})
    course = course_map.get(offering.course_id)
    if course:
        resp.course_code = course.course_code
        resp.course_name = course.course_name
    return resp


@router.post("/", response_model=SingleResponse[OfferingResponse])
async def create_offering(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:create"))],
    request: OfferingCreateRequest,
) -> SingleResponse[OfferingResponse]:
    """Create a new offering."""
    audit = AuditContext(audit_db, current_user, "offering", action="offering_created")
    try:
        offering = await course_management_service.create_offering(db, request)
        await audit.log_success(target_id=str(offering.id))
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=await _enrich_offering(db, offering))


@router.get("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def get_offering(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:read"))],
    offering_id: int,
) -> SingleResponse[OfferingResponse]:
    """Get offering detail."""
    offering = await course_management_service.get_offering(db, offering_id)
    return SingleResponse(data=await _enrich_offering(db, offering))


@router.put("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def update_offering(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:update"))],
    offering_id: int,
    request: OfferingUpdateRequest,
) -> SingleResponse[OfferingResponse]:
    """Full update offering (assigned teachers or admin only)."""
    await _check_offering_access(current_user, db, offering_id)
    audit = AuditContext(audit_db, current_user, "offering",
                         target_id=str(offering_id), action="offering_updated")
    try:
        offering = await course_management_service.update_offering(db, offering_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=await _enrich_offering(db, offering))


@router.patch("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def patch_offering(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:update"))],
    offering_id: int,
    request: OfferingPatchRequest,
) -> SingleResponse[OfferingResponse]:
    """Partial update offering (assigned teachers or admin only)."""
    await _check_offering_access(current_user, db, offering_id)
    audit = AuditContext(audit_db, current_user, "offering",
                         target_id=str(offering_id), action="offering_updated")
    try:
        offering = await course_management_service.update_offering(db, offering_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=await _enrich_offering(db, offering))


@router.delete("/{offering_id}", response_model=APIResponse[None])
async def delete_offering(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:delete"))],
    offering_id: int,
) -> APIResponse[None]:
    """Delete offering (assigned teachers or admin only)."""
    await _check_offering_access(current_user, db, offering_id)
    audit = AuditContext(audit_db, current_user, "offering",
                         target_id=str(offering_id), action="offering_deleted")
    try:
        await course_management_service.delete_offering(db, offering_id)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)
