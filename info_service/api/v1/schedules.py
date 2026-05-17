"""Info Service — /schedules/* endpoints (including teacher sub-resource)."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.schedule_schema import (
    ScheduleCreateRequest,
    SchedulePatchRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
    TeacherAssignmentCreateRequest,
    TeacherAssignmentResponse,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["schedules"])


# ---- Schedule CRUD ----


@router.get("/", response_model=ListResponse[ScheduleResponse])
async def list_schedules(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    offering_id: int | None = Query(default=None),
) -> ListResponse[ScheduleResponse]:
    """Get paginated schedule list."""
    warnings.warn("TODO: implement GET /schedules")
    raise NotImplementedError("GET /schedules not implemented")


@router.post("/", response_model=SingleResponse[ScheduleResponse])
async def create_schedule(request: ScheduleCreateRequest) -> SingleResponse[ScheduleResponse]:
    """Create a schedule entry (with conflict check)."""
    warnings.warn("TODO: implement POST /schedules")
    raise NotImplementedError("POST /schedules not implemented")


@router.get("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def get_schedule(schedule_id: int) -> SingleResponse[ScheduleResponse]:
    """Get schedule detail."""
    warnings.warn("TODO: implement GET /schedules/{id}")
    raise NotImplementedError("GET /schedules/{id} not implemented")


@router.put("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def update_schedule(
    schedule_id: int, request: ScheduleUpdateRequest
) -> SingleResponse[ScheduleResponse]:
    """Full update schedule."""
    warnings.warn("TODO: implement PUT /schedules/{id}")
    raise NotImplementedError("PUT /schedules/{id} not implemented")


@router.patch("/{schedule_id}", response_model=SingleResponse[ScheduleResponse])
async def patch_schedule(
    schedule_id: int, request: SchedulePatchRequest
) -> SingleResponse[ScheduleResponse]:
    """Partial update schedule."""
    warnings.warn("TODO: implement PATCH /schedules/{id}")
    raise NotImplementedError("PATCH /schedules/{id} not implemented")


@router.delete("/{schedule_id}", response_model=APIResponse[None])
async def delete_schedule(schedule_id: int) -> APIResponse[None]:
    """Delete schedule."""
    warnings.warn("TODO: implement DELETE /schedules/{id}")
    raise NotImplementedError("DELETE /schedules/{id} not implemented")


# ---- Teacher assignments (sub-resource of schedules) ----


@router.get("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def list_teachers(schedule_id: int) -> ListResponse[TeacherAssignmentResponse]:
    """List teachers assigned to a schedule."""
    warnings.warn("TODO: implement GET /schedules/{id}/teachers")
    raise NotImplementedError("GET /schedules/{id}/teachers not implemented")


@router.put("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def replace_teachers(
    schedule_id: int, teacher_ids: list[str]
) -> ListResponse[TeacherAssignmentResponse]:
    """Replace all teacher assignments."""
    warnings.warn("TODO: implement PUT /schedules/{id}/teachers")
    raise NotImplementedError("PUT /schedules/{id}/teachers not implemented")


@router.post("/{schedule_id}/teachers", response_model=ListResponse[TeacherAssignmentResponse])
async def add_teachers(
    schedule_id: int, teacher_ids: list[str]
) -> ListResponse[TeacherAssignmentResponse]:
    """Add teachers to schedule."""
    warnings.warn("TODO: implement POST /schedules/{id}/teachers")
    raise NotImplementedError("POST /schedules/{id}/teachers not implemented")


@router.put(
    "/{schedule_id}/teachers/{teacher_id}",
    response_model=SingleResponse[TeacherAssignmentResponse],
)
async def assign_teacher(
    schedule_id: int, teacher_id: str, request: TeacherAssignmentCreateRequest
) -> SingleResponse[TeacherAssignmentResponse]:
    """Assign a single teacher."""
    warnings.warn("TODO: implement PUT /schedules/{id}/teachers/{tid}")
    raise NotImplementedError("PUT /schedules/{id}/teachers/{tid} not implemented")


@router.delete("/{schedule_id}/teachers/{teacher_id}", response_model=APIResponse[None])
async def remove_teacher(schedule_id: int, teacher_id: str) -> APIResponse[None]:
    """Remove a teacher assignment."""
    warnings.warn("TODO: implement DELETE /schedules/{id}/teachers/{tid}")
    raise NotImplementedError("DELETE /schedules/{id}/teachers/{tid} not implemented")
