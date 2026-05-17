"""Info Service — /courses/* endpoints."""

import warnings

from fastapi import APIRouter, Query

from info_service.schemas.course_schema import (
    CourseCreateRequest,
    CoursePatchRequest,
    CourseResponse,
    CourseUpdateRequest,
)
from shared.response import APIResponse, ListResponse, SingleResponse

router = APIRouter(tags=["courses"])


@router.get("/", response_model=ListResponse[CourseResponse])
async def list_courses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> ListResponse[CourseResponse]:
    """Get paginated course list."""
    warnings.warn("TODO: implement GET /courses")
    raise NotImplementedError("GET /courses not implemented")


@router.post("/", response_model=SingleResponse[CourseResponse])
async def create_course(request: CourseCreateRequest) -> SingleResponse[CourseResponse]:
    """Create a new course."""
    warnings.warn("TODO: implement POST /courses")
    raise NotImplementedError("POST /courses not implemented")


@router.get("/{course_id}", response_model=SingleResponse[CourseResponse])
async def get_course(course_id: int) -> SingleResponse[CourseResponse]:
    """Get course detail."""
    warnings.warn("TODO: implement GET /courses/{id}")
    raise NotImplementedError("GET /courses/{id} not implemented")


@router.put("/{course_id}", response_model=SingleResponse[CourseResponse])
async def update_course(
    course_id: int, request: CourseUpdateRequest
) -> SingleResponse[CourseResponse]:
    """Full update course."""
    warnings.warn("TODO: implement PUT /courses/{id}")
    raise NotImplementedError("PUT /courses/{id} not implemented")


@router.patch("/{course_id}", response_model=SingleResponse[CourseResponse])
async def patch_course(
    course_id: int, request: CoursePatchRequest
) -> SingleResponse[CourseResponse]:
    """Partial update course."""
    warnings.warn("TODO: implement PATCH /courses/{id}")
    raise NotImplementedError("PATCH /courses/{id} not implemented")


@router.delete("/{course_id}", response_model=APIResponse[None])
async def delete_course(course_id: int) -> APIResponse[None]:
    """Delete course."""
    warnings.warn("TODO: implement DELETE /courses/{id}")
    raise NotImplementedError("DELETE /courses/{id} not implemented")
