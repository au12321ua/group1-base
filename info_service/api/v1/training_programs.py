"""Info Service — /training-programs/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.training_program_schema import (
    TrainingProgramCreateRequest,
    TrainingProgramPatchRequest,
    TrainingProgramResponse,
    TrainingProgramUpdateRequest,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["training-programs"])


@router.get("/", response_model=ListResponse[TrainingProgramResponse])
async def list_training_programs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ListResponse[TrainingProgramResponse]:
    """Get paginated training program list."""
    warnings.warn("TODO: implement GET /training-programs")
    raise NotImplementedError("GET /training-programs not implemented")


@router.post("/", response_model=SingleResponse[TrainingProgramResponse])
async def create_training_program(
    request: TrainingProgramCreateRequest,
) -> SingleResponse[TrainingProgramResponse]:
    """Create a training program."""
    warnings.warn("TODO: implement POST /training-programs")
    raise NotImplementedError("POST /training-programs not implemented")


@router.get("/by-major", response_model=ListResponse[TrainingProgramResponse])
async def get_by_major(
    major_code: str = Query(...),
    grade: str | None = Query(default=None),
) -> ListResponse[TrainingProgramResponse]:
    """Get training programs by major code and optionally grade."""
    warnings.warn("TODO: implement GET /training-programs/by-major")
    raise NotImplementedError("GET /training-programs/by-major not implemented")


@router.get("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def get_training_program(program_id: int) -> SingleResponse[TrainingProgramResponse]:
    """Get training program detail."""
    warnings.warn("TODO: implement GET /training-programs/{id}")
    raise NotImplementedError("GET /training-programs/{id} not implemented")


@router.put("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def update_training_program(
    program_id: int, request: TrainingProgramUpdateRequest
) -> SingleResponse[TrainingProgramResponse]:
    """Full update training program."""
    warnings.warn("TODO: implement PUT /training-programs/{id}")
    raise NotImplementedError("PUT /training-programs/{id} not implemented")


@router.patch("/{program_id}", response_model=SingleResponse[TrainingProgramResponse])
async def patch_training_program(
    program_id: int, request: TrainingProgramPatchRequest
) -> SingleResponse[TrainingProgramResponse]:
    """Partial update training program."""
    warnings.warn("TODO: implement PATCH /training-programs/{id}")
    raise NotImplementedError("PATCH /training-programs/{id} not implemented")


@router.delete("/{program_id}", response_model=APIResponse[None])
async def delete_training_program(program_id: int) -> APIResponse[None]:
    """Delete training program."""
    warnings.warn("TODO: implement DELETE /training-programs/{id}")
    raise NotImplementedError("DELETE /training-programs/{id} not implemented")
