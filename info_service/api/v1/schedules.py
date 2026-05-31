"""Info Service — /schedules/* endpoints (including teacher sub-resource)."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query

from info_service.api.deps import InfoDbSession
from info_service.core.security import check_resource_access
from info_service.deps import require_permission
from info_service.schemas.schedule_schema import (
    ScheduleCreateRequest,
    SchedulePatchRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
    TeacherAssignmentCreateRequest,
    TeacherAssignmentResponse,
)
from info_service.services.course_management_service import course_management_service
from shared.exceptions import AuthorizationError
from shared.response import (
    APIResponse,
    ListResponse,
    PaginatedData,
    PaginationMeta,
    SingleResponse,
)
from shared.security import IdentityContext

router = APIRouter(tags=["schedules"])


# ---- Schedule CRUD ----


def _teacher_assignment_list_response(items) -> ListResponse[TeacherAssignmentResponse]:
    """Wrap teacher assignments in the common paginated response shape."""
    return ListResponse(
        data=PaginatedData(
            items=[TeacherAssignmentResponse.model_validate(item) for item in items],
            pagination=PaginationMeta(total=len(items), page=1, page_size=len(items)),
        )
    )


async def _check_schedule_access(current_user: IdentityContext, db, schedule_id: int) -> None:
    """Verify the current user can modify the schedule (assigned teacher or admin)."""
    schedule = await course_management_service.get_schedule(db, schedule_id)
    offering = await course_management_service.get_offering(db, schedule.offering_id)
    teacher_ids = [t for t in offering.teacher_ids.split(",") if t]
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_teacher_ids=teacher_ids,
    ):
        raise AuthorizationError(
            "Access denied: only assigned teachers or administrators can modify this schedule"
        )


@router.get("/", response_model=ListResponse[ScheduleResponse])
async def list_schedules(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    offering_id: int | None = Query(default=None),
) -> ListResponse[ScheduleResponse]:
    """Get paginated schedule list."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_schedules(
        db,
        skip=skip,
        limit=page_size,
        offering_id=offering_id,
    )
    return ListResponse(
        data=PaginatedData(
            items=[ScheduleResponse.model_validate(item) for item in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[ScheduleResponse])
async def create_schedule(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:create"))],
    request: ScheduleCreateRequest,
) -> SingleResponse[ScheduleResponse]:
    """Create a schedule entry (with conflict check)."""
    schedule = await course_management_service.create_schedule(db, request)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.get("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def get_schedule(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:read"))],
    schedule_id: int,
) -> SingleResponse[ScheduleResponse]:
    """Get schedule detail."""
    schedule = await course_management_service.get_schedule(db, schedule_id)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.put("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def update_schedule(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:update"))],
    schedule_id: int,
    request: ScheduleUpdateRequest,
) -> SingleResponse[ScheduleResponse]:
    """Full update schedule (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    schedule = await course_management_service.update_schedule(db, schedule_id, request)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.patch("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def patch_schedule(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:update"))],
    schedule_id: int,
    request: SchedulePatchRequest,
) -> SingleResponse[ScheduleResponse]:
    """Partial update schedule (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    schedule = await course_management_service.update_schedule(db, schedule_id, request)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.delete("/{schedule_id}", response_model=APIResponse[None])
async def delete_schedule(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:delete"))],
    schedule_id: int,
) -> APIResponse[None]:
    """Delete schedule (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    await course_management_service.delete_schedule(db, schedule_id)
    return APIResponse(data=None)


# ---- Teacher assignments (sub-resource of schedules) ----


@router.get("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def list_teachers(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:read"))],
    schedule_id: int,
) -> ListResponse[TeacherAssignmentResponse]:
    """List teachers assigned to a schedule."""
    items = await course_management_service.list_teachers_for_schedule(db, schedule_id)
    return _teacher_assignment_list_response(items)


@router.put("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def replace_teachers(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:update"))],
    schedule_id: int,
    teacher_ids: list[str] = Body(...),
) -> ListResponse[TeacherAssignmentResponse]:
    """Replace all teacher assignments (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    items = await course_management_service.replace_teachers(db, schedule_id, teacher_ids)
    return _teacher_assignment_list_response(items)


@router.post("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def add_teachers(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:update"))],
    schedule_id: int,
    teacher_ids: list[str] = Body(...),
) -> ListResponse[TeacherAssignmentResponse]:
    """Add teachers to schedule (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    items = await course_management_service.add_teachers(db, schedule_id, teacher_ids)
    return _teacher_assignment_list_response(items)


@router.put(
    "/{schedule_id}/teachers/{teacher_id}",
    response_model=SingleResponse[TeacherAssignmentResponse],
)
async def assign_teacher(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:update"))],
    schedule_id: int,
    teacher_id: str,
    request: TeacherAssignmentCreateRequest,
) -> SingleResponse[TeacherAssignmentResponse]:
    """Assign a single teacher (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    normalized_teacher_id = teacher_id.strip()
    if request.teacher_id.strip() != normalized_teacher_id:
        from shared.exceptions import BusinessRuleError

        raise BusinessRuleError("teacher_id in path and body must match")
    assignment = await course_management_service.assign_teacher(
        db,
        schedule_id,
        normalized_teacher_id,
        request.role_type,
    )
    return SingleResponse(data=TeacherAssignmentResponse.model_validate(assignment))


@router.delete("/{schedule_id}/teachers/{teacher_id}", response_model=APIResponse[None])
async def remove_teacher(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("schedule:delete"))],
    schedule_id: int,
    teacher_id: str,
) -> APIResponse[None]:
    """Remove a teacher assignment (assigned teachers or admin only)."""
    await _check_schedule_access(current_user, db, schedule_id)
    await course_management_service.remove_teacher(db, schedule_id, teacher_id)
    return APIResponse(data=None)
