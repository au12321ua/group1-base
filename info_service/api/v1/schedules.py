"""Info Service — /schedules/* endpoints (including teacher sub-resource)."""

from fastapi import APIRouter, Body, Query

from info_service.api.deps import InfoDbSession
from info_service.schemas.schedule_schema import (
    ScheduleCreateRequest,
    SchedulePatchRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
    TeacherAssignmentCreateRequest,
    TeacherAssignmentResponse,
)
from info_service.services.course_management_service import course_management_service
from shared.response import (
    APIResponse,
    ListResponse,
    PaginatedData,
    PaginationMeta,
    SingleResponse,
)

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


@router.get("/", response_model=ListResponse[ScheduleResponse])
async def list_schedules(
    db: InfoDbSession,
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
    request: ScheduleCreateRequest,
) -> SingleResponse[ScheduleResponse]:
    """Create a schedule entry (with conflict check)."""
    schedule = await course_management_service.create_schedule(db, request)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.get("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def get_schedule(
    db: InfoDbSession,
    schedule_id: int,
) -> SingleResponse[ScheduleResponse]:
    """Get schedule detail."""
    schedule = await course_management_service.get_schedule(db, schedule_id)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.put("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def update_schedule(
    db: InfoDbSession,
    schedule_id: int,
    request: ScheduleUpdateRequest,
) -> SingleResponse[ScheduleResponse]:
    """Full update schedule."""
    schedule = await course_management_service.update_schedule(db, schedule_id, request)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.patch("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def patch_schedule(
    db: InfoDbSession,
    schedule_id: int,
    request: SchedulePatchRequest,
) -> SingleResponse[ScheduleResponse]:
    """Partial update schedule."""
    schedule = await course_management_service.update_schedule(db, schedule_id, request)
    return SingleResponse(data=ScheduleResponse.model_validate(schedule))


@router.delete("/{schedule_id}", response_model=APIResponse[None])
async def delete_schedule(
    db: InfoDbSession,
    schedule_id: int,
) -> APIResponse[None]:
    """Delete schedule."""
    await course_management_service.delete_schedule(db, schedule_id)
    return APIResponse(data=None)


# ---- Teacher assignments (sub-resource of schedules) ----


@router.get("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def list_teachers(
    db: InfoDbSession,
    schedule_id: int,
) -> ListResponse[TeacherAssignmentResponse]:
    """List teachers assigned to a schedule."""
    items = await course_management_service.list_teachers_for_schedule(db, schedule_id)
    return _teacher_assignment_list_response(items)


@router.put("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def replace_teachers(
    db: InfoDbSession,
    schedule_id: int,
    teacher_ids: list[str] = Body(...),
) -> ListResponse[TeacherAssignmentResponse]:
    """Replace all teacher assignments."""
    items = await course_management_service.replace_teachers(db, schedule_id, teacher_ids)
    return _teacher_assignment_list_response(items)


@router.post("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def add_teachers(
    db: InfoDbSession,
    schedule_id: int,
    teacher_ids: list[str] = Body(...),
) -> ListResponse[TeacherAssignmentResponse]:
    """Add teachers to schedule."""
    items = await course_management_service.add_teachers(db, schedule_id, teacher_ids)
    return _teacher_assignment_list_response(items)


@router.put(
    "/{schedule_id}/teachers/{teacher_id}",
    response_model=SingleResponse[TeacherAssignmentResponse],
)
async def assign_teacher(
    db: InfoDbSession,
    schedule_id: int,
    teacher_id: str,
    request: TeacherAssignmentCreateRequest,
) -> SingleResponse[TeacherAssignmentResponse]:
    """Assign a single teacher."""
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
    schedule_id: int,
    teacher_id: str,
) -> APIResponse[None]:
    """Remove a teacher assignment."""
    await course_management_service.remove_teacher(db, schedule_id, teacher_id)
    return APIResponse(data=None)
