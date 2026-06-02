"""Info Service — /classrooms/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.audit import AuditContext
from info_service.deps import require_permission
from info_service.schemas.classroom_schema import (
    ClassroomCreateRequest,
    ClassroomPatchRequest,
    ClassroomResponse,
    ClassroomUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import AppError
from shared.response import (
    APIResponse,
    ListResponse,
    PaginatedData,
    PaginationMeta,
    SingleResponse,
)
from shared.security import IdentityContext

router = APIRouter(tags=["classrooms"])


@router.get("/", response_model=ListResponse[ClassroomResponse])
async def list_classrooms(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("classroom:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
    building: str | None = Query(default=None),
    classroom_type: str | None = Query(default=None),
    min_capacity: int | None = Query(default=None),
) -> ListResponse[ClassroomResponse]:
    """Get paginated classroom list."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_classrooms(
        db,
        skip=skip,
        limit=page_size,
        keyword=keyword,
        building=building,
        classroom_type=classroom_type,
        min_capacity=min_capacity,
    )
    return ListResponse(
        data=PaginatedData(
            items=[ClassroomResponse.model_validate(item) for item in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[ClassroomResponse])
async def create_classroom(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("classroom:create"))],
    request: ClassroomCreateRequest,
) -> SingleResponse[ClassroomResponse]:
    """Create a new classroom."""
    audit = AuditContext(audit_db, current_user, "classroom", action="classroom_created")
    try:
        classroom = await course_management_service.create_classroom(db, request)
        await audit.log_success(target_id=str(classroom.id))
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=ClassroomResponse.model_validate(classroom))


@router.get("/{classroom_id}", response_model=SingleResponse[ClassroomResponse])
async def get_classroom(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("classroom:read"))],
    classroom_id: int,
) -> SingleResponse[ClassroomResponse]:
    """Get classroom detail."""
    classroom = await course_management_service.get_classroom(db, classroom_id)
    return SingleResponse(data=ClassroomResponse.model_validate(classroom))


@router.put("/{classroom_id}", response_model=SingleResponse[ClassroomResponse])
async def update_classroom(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("classroom:update"))],
    classroom_id: int,
    request: ClassroomUpdateRequest,
) -> SingleResponse[ClassroomResponse]:
    """Full update classroom."""
    audit = AuditContext(audit_db, current_user, "classroom",
                         target_id=str(classroom_id), action="classroom_updated")
    try:
        classroom = await course_management_service.update_classroom(db, classroom_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=ClassroomResponse.model_validate(classroom))


@router.patch("/{classroom_id}", response_model=SingleResponse[ClassroomResponse])
async def patch_classroom(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("classroom:update"))],
    classroom_id: int,
    request: ClassroomPatchRequest,
) -> SingleResponse[ClassroomResponse]:
    """Partial update classroom."""
    audit = AuditContext(audit_db, current_user, "classroom",
                         target_id=str(classroom_id), action="classroom_updated")
    try:
        classroom = await course_management_service.patch_classroom(db, classroom_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=ClassroomResponse.model_validate(classroom))


@router.delete("/{classroom_id}", response_model=APIResponse[None])
async def delete_classroom(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("classroom:delete"))],
    classroom_id: int,
) -> APIResponse[None]:
    """Delete classroom."""
    audit = AuditContext(audit_db, current_user, "classroom",
                         target_id=str(classroom_id), action="classroom_deleted")
    try:
        await course_management_service.delete_classroom(db, classroom_id)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)
