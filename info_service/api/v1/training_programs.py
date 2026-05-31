"""Info Service — /training-programs/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import InfoDbSession
from info_service.deps import require_admin, require_permission
from info_service.schemas.training_program_schema import (
    TrainingProgramCreateRequest,
    TrainingProgramPatchRequest,
    TrainingProgramResponse,
    TrainingProgramUpdateRequest,
)
from info_service.services.course_management_service import course_management_service
from shared.response import (
    APIResponse,
    ListResponse,
    PaginatedData,
    PaginationMeta,
    SingleResponse,
)
from shared.security import IdentityContext

router = APIRouter(tags=["training-programs"])


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
    return ListResponse(
        data=PaginatedData(
            items=[TrainingProgramResponse.model_validate(item) for item in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[TrainingProgramResponse])
async def create_training_program(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:create"))],
    request: TrainingProgramCreateRequest,
) -> SingleResponse[TrainingProgramResponse]:
    """Create a training program."""
    program = await course_management_service.create_training_program(db, request)
    return SingleResponse(data=TrainingProgramResponse.model_validate(program))


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
    return ListResponse(
        data=PaginatedData(
            items=[TrainingProgramResponse.model_validate(item) for item in items],
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
    return SingleResponse(data=TrainingProgramResponse.model_validate(program))


@router.put("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def update_training_program(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:update"))],
    program_id: int,
    request: TrainingProgramUpdateRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[TrainingProgramResponse]:
    """Full update training program (admin only)."""
    program = await course_management_service.update_training_program(db, program_id, request)
    return SingleResponse(data=TrainingProgramResponse.model_validate(program))


@router.patch("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def patch_training_program(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:update"))],
    program_id: int,
    request: TrainingProgramPatchRequest,
    _admin: None = Depends(require_admin),
) -> SingleResponse[TrainingProgramResponse]:
    """Partial update training program (admin only)."""
    program = await course_management_service.update_training_program(db, program_id, request)
    return SingleResponse(data=TrainingProgramResponse.model_validate(program))


@router.delete("/{program_id}", response_model=APIResponse[None])
async def delete_training_program(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("training:delete"))],
    program_id: int,
    _admin: None = Depends(require_admin),
) -> APIResponse[None]:
    """Delete training program (admin only)."""
    await course_management_service.delete_training_program(db, program_id)
    return APIResponse(data=None)
