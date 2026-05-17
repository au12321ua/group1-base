"""Info Service — /data-provision/* endpoints (for B/C/F system consumption)."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.data_provision_schema import (
    DataProvisionWrapper,
)
from shared.response import APIResponse

router = APIRouter(tags=["data-provision"])


@router.get("/teachers", response_model=APIResponse[DataProvisionWrapper])
async def list_teachers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Get teacher list with snapshot metadata (for B 排课 system, Service Token auth)."""
    warnings.warn("TODO: implement GET /data-provision/teachers")
    raise NotImplementedError("GET /data-provision/teachers not implemented")


@router.get("/candidate-students", response_model=APIResponse[DataProvisionWrapper])
async def list_candidate_students(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Get candidate student list (for B 排课 system, Service Token auth)."""
    warnings.warn("TODO: implement GET /data-provision/candidate-students")
    raise NotImplementedError("GET /data-provision/candidate-students not implemented")


@router.get("/calendars", response_model=APIResponse[DataProvisionWrapper])
async def get_calendars() -> APIResponse[DataProvisionWrapper]:
    """Get academic calendars (for B 排课 system, Service Token auth)."""
    warnings.warn("TODO: implement GET /data-provision/calendars")
    raise NotImplementedError("GET /data-provision/calendars not implemented")


@router.get("/training-programs", response_model=APIResponse[DataProvisionWrapper])
async def list_training_programs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Get training programs (for C 选课 system, Service Token auth)."""
    warnings.warn("TODO: implement GET /data-provision/training-programs")
    raise NotImplementedError("GET /data-provision/training-programs not implemented")


@router.get("/selected-students", response_model=APIResponse[DataProvisionWrapper])
async def query_selected_students(
    course_id: int | None = Query(default=None),
    term_code: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
) -> APIResponse[DataProvisionWrapper]:
    """Proxy query selected students from C system (for B 排课 system)."""
    warnings.warn("TODO: implement GET /data-provision/selected-students — proxy to C system")
    raise NotImplementedError("GET /data-provision/selected-students not implemented")
