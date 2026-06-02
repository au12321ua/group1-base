"""Info Service — /courses/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.audit import AuditContext
from info_service.crud.course_crud import course_crud
from info_service.deps import require_admin, require_permission
from info_service.schemas.course_schema import (
    CourseCreateRequest,
    CoursePatchRequest,
    CoursePrerequisiteCreateRequest,
    CoursePrerequisiteResponse,
    CourseResponse,
    CourseUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import AppError, BusinessRuleError
from shared.response import (
    APIResponse,
    ListResponse,
    PaginatedData,
    PaginationMeta,
    SingleResponse,
)
from shared.security import IdentityContext

router = APIRouter(tags=["courses"])


@router.get("/", response_model=ListResponse[CourseResponse])
async def list_courses(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> ListResponse[CourseResponse]:
    """Get paginated course list."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_courses(
        db,
        skip=skip,
        limit=page_size,
        keyword=keyword,
        is_active=is_active,
    )
    return ListResponse(
        data=PaginatedData(
            items=[CourseResponse.model_validate(item) for item in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[CourseResponse])
async def create_course(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:create"))],
    request: CourseCreateRequest,
) -> SingleResponse[CourseResponse]:
    """Create a new course."""
    audit = AuditContext(audit_db, current_user, "course", action="course_created")
    try:
        course = await course_management_service.create_course(db, request)
        await audit.log_success(target_id=str(course.id))
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=CourseResponse.model_validate(course))


@router.get("/{course_id}", response_model=SingleResponse[CourseResponse])
async def get_course(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:read"))],
    course_id: int,
) -> SingleResponse[CourseResponse]:
    """Get course detail."""
    course = await course_management_service.get_course(db, course_id)
    return SingleResponse(data=CourseResponse.model_validate(course))


@router.put("/{course_id}", response_model=SingleResponse[CourseResponse])
async def update_course(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:update"))],
    course_id: int,
    request: CourseUpdateRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[CourseResponse]:
    """Full update course (admin only)."""
    audit = AuditContext(audit_db, current_user, "course",
                         target_id=str(course_id), action="course_updated")
    try:
        course = await course_management_service.update_course(db, course_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=CourseResponse.model_validate(course))


@router.patch("/{course_id}", response_model=SingleResponse[CourseResponse])
async def patch_course(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:update"))],
    course_id: int,
    request: CoursePatchRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[CourseResponse]:
    """Partial update course (admin only)."""
    audit = AuditContext(audit_db, current_user, "course",
                         target_id=str(course_id), action="course_updated")
    try:
        course = await course_management_service.update_course(db, course_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=CourseResponse.model_validate(course))


@router.delete("/{course_id}", response_model=APIResponse[None])
async def delete_course(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:delete"))],
    course_id: int,
    _admin: None = Depends(require_admin),
) -> APIResponse[None]:
    """Delete course (admin only)."""
    audit = AuditContext(audit_db, current_user, "course",
                         target_id=str(course_id), action="course_deleted")
    try:
        await course_management_service.delete_course(db, course_id)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)


# ---- Prerequisites (sub-resource of courses) ----


@router.get("/{course_id}/prerequisites", response_model=ListResponse[CoursePrerequisiteResponse])
async def list_prerequisites(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:read"))],
    course_id: int,
) -> ListResponse[CoursePrerequisiteResponse]:
    """List prerequisites for a course."""
    items = await course_crud.list_prerequisites(db, course_id)
    course_ids = {p.prerequisite_course_id for p in items}
    course_map = await course_management_service.batch_get_courses(db, course_ids)
    result = []
    for p in items:
        resp = CoursePrerequisiteResponse.model_validate(p)
        course = course_map.get(p.prerequisite_course_id)
        if course:
            resp.prerequisite_course_code = course.course_code
            resp.prerequisite_course_name = course.course_name
        result.append(resp)
    return ListResponse(
        data=PaginatedData(
            items=result,
            pagination=PaginationMeta(total=len(result), page=1, page_size=len(result)),
        )
    )


@router.post(
    "/{course_id}/prerequisites",
    response_model=SingleResponse[CoursePrerequisiteResponse],
)
async def add_prerequisite(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:update"))],
    course_id: int,
    request: CoursePrerequisiteCreateRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[CoursePrerequisiteResponse]:
    """Add a prerequisite to a course (admin only)."""
    audit = AuditContext(audit_db, current_user, "course",
                         target_id=str(course_id),
                         action="prerequisite_added",
                         reason=f"prereq_id={request.prerequisite_course_id}")
    try:
        prereq = await course_crud.add_prerequisite(
            db,
            course_id=course_id,
            prerequisite_course_id=request.prerequisite_course_id,
            min_grade=request.min_grade,
        )
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    # Enrich with prerequisite course code/name
    course_map = await course_management_service.batch_get_courses(
        db, {prereq.prerequisite_course_id}
    )
    resp = CoursePrerequisiteResponse.model_validate(prereq)
    course = course_map.get(prereq.prerequisite_course_id)
    if course:
        resp.prerequisite_course_code = course.course_code
        resp.prerequisite_course_name = course.course_name
    return SingleResponse(data=resp)


@router.delete(
    "/{course_id}/prerequisites/{prerequisite_course_id}",
    response_model=APIResponse[None],
)
async def remove_prerequisite(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:delete"))],
    course_id: int,
    prerequisite_course_id: int,
    _admin: None = Depends(require_admin),
) -> APIResponse[None]:
    """Remove a prerequisite from a course (admin only)."""
    audit = AuditContext(audit_db, current_user, "course",
                         target_id=str(course_id),
                         action="prerequisite_removed",
                         reason=f"prereq_id={prerequisite_course_id}")
    try:
        removed = await course_crud.remove_prerequisite(
            db,
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
        )
        if not removed:
            raise BusinessRuleError("Prerequisite relation not found")
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)
