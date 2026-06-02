"""Info Service — /training-programs/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.audit import AuditContext
from info_service.crud.training_program_crud import training_program_crud
from info_service.deps import require_admin, require_permission
from info_service.schemas.training_program_schema import (
    CourseBrief,
    TrainingProgramCreateRequest,
    TrainingProgramPatchRequest,
    TrainingProgramResponse,
    TrainingProgramUpdateRequest,
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

router = APIRouter(tags=["training-programs"])


async def _build_program_response(
    db, program, course_ids: list[int] | None = None,
    course_map: dict | None = None,
) -> TrainingProgramResponse:
    """Assemble response with required_course_ids and required_courses from the association table.

    If *course_ids* is provided the DB query is skipped (batch path).
    If *course_map* is provided, builds CourseBrief entries (batch path).
    """
    if course_ids is None:
        associations = await training_program_crud.get_courses_by_program(db, program.id)
        course_ids = [assoc.course_id for assoc in associations]
    resp = TrainingProgramResponse.model_validate(program)
    resp.required_course_ids = course_ids
    # Build enriched course list
    if course_ids:
        if course_map is None:
            course_map = await course_management_service.batch_get_courses(db, set(course_ids))

        resp.required_courses = [
            CourseBrief(id=cid, course_code=c.course_code, course_name=c.course_name)
            for cid in course_ids
            if (c := course_map.get(cid))
        ]
    return resp


@router.get("/", response_model=ListResponse[TrainingProgramResponse])
async def list_training_programs(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ListResponse[TrainingProgramResponse]:
    """Get paginated training program list."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_training_programs(
        db,
        skip=skip,
        limit=page_size,
    )
    # Batch-fetch course associations for all programs in one query
    program_ids = [p.id for p in items]
    course_id_map = await training_program_crud.get_course_ids_by_programs(db, program_ids)
    # Batch-fetch course details for enrichment
    all_course_ids: set[int] = set()
    for cids in course_id_map.values():
        all_course_ids.update(cids)
    course_map = await course_management_service.batch_get_courses(db, all_course_ids)
    return ListResponse(
        data=PaginatedData(
            items=[
                await _build_program_response(
                    db, p, course_id_map.get(p.id, []), course_map=course_map
                )
                for p in items
            ],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[TrainingProgramResponse])
async def create_training_program(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:create"))],
    request: TrainingProgramCreateRequest,
) -> SingleResponse[TrainingProgramResponse]:
    """Create a training program."""
    audit = AuditContext(audit_db, current_user, "training_program",
                         action="training_program_created")
    try:
        program = await course_management_service.create_training_program(db, request)
        await audit.log_success(target_id=str(program.id))
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=await _build_program_response(db, program))


@router.get("/by-major", response_model=ListResponse[TrainingProgramResponse])
async def get_by_major(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    major_code: str = Query(...),
    grade: str | None = Query(default=None),
) -> ListResponse[TrainingProgramResponse]:
    """Get training programs by major code and optionally grade."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_training_programs(
        db,
        skip=skip,
        limit=page_size,
        major_code=major_code,
        grade=grade,
    )
    program_ids = [p.id for p in items]
    course_id_map = await training_program_crud.get_course_ids_by_programs(db, program_ids)
    all_course_ids: set[int] = set()
    for cids in course_id_map.values():
        all_course_ids.update(cids)
    course_map = await course_management_service.batch_get_courses(db, all_course_ids)
    return ListResponse(
        data=PaginatedData(
            items=[
                await _build_program_response(
                    db, p, course_id_map.get(p.id, []), course_map=course_map
                )
                for p in items
            ],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.get("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def get_training_program(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:read"))],
    program_id: int,
) -> SingleResponse[TrainingProgramResponse]:
    """Get training program detail."""
    program = await course_management_service.get_training_program(db, program_id)
    return SingleResponse(data=await _build_program_response(db, program))


@router.put("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def update_training_program(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:update"))],
    program_id: int,
    request: TrainingProgramUpdateRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[TrainingProgramResponse]:
    """Full update training program (admin only)."""
    audit = AuditContext(audit_db, current_user, "training_program",
                         target_id=str(program_id), action="training_program_updated")
    try:
        program = await course_management_service.update_training_program(db, program_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=await _build_program_response(db, program))


@router.patch("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def patch_training_program(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:update"))],
    program_id: int,
    request: TrainingProgramPatchRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[TrainingProgramResponse]:
    """Partial update training program (admin only)."""
    audit = AuditContext(audit_db, current_user, "training_program",
                         target_id=str(program_id), action="training_program_updated")
    try:
        program = await course_management_service.update_training_program(db, program_id, request)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return SingleResponse(data=await _build_program_response(db, program))


@router.delete("/{program_id}", response_model=APIResponse[None])
async def delete_training_program(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:delete"))],
    program_id: int,
    _admin: None = Depends(require_admin),
) -> APIResponse[None]:
    """Delete training program (admin only)."""
    audit = AuditContext(audit_db, current_user, "training_program",
                         target_id=str(program_id), action="training_program_deleted")
    try:
        await course_management_service.delete_training_program(db, program_id)
        await audit.log_success()
    except AppError as exc:
        await audit.log_failure(str(exc.message))
        raise
    return APIResponse(data=None)
