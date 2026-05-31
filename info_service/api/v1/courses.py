"""Info Service — /courses/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import InfoDbSession
from info_service.core.security import check_resource_access
from info_service.deps import require_permission
from info_service.schemas.course_schema import (
    CourseCreateRequest,
    CoursePatchRequest,
    CourseResponse,
    CourseUpdateRequest,
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
    current_user: Annotated[IdentityContext, Depends(require_permission("course:create"))],
    request: CourseCreateRequest,
) -> SingleResponse[CourseResponse]:
    """Create a new course."""
    course = await course_management_service.create_course(db, request)
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
    current_user: Annotated[IdentityContext, Depends(require_permission("course:update"))],
    course_id: int,
    request: CourseUpdateRequest,
) -> SingleResponse[CourseResponse]:
    """Full update course (admin only)."""
    if not check_resource_access(current_user.user_id, current_user.role):
        raise AuthorizationError("Access denied: only administrators can modify courses")
    course = await course_management_service.update_course(db, course_id, request)
    return SingleResponse(data=CourseResponse.model_validate(course))


@router.patch("/{course_id}", response_model=SingleResponse[CourseResponse])
async def patch_course(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:update"))],
    course_id: int,
    request: CoursePatchRequest,
) -> SingleResponse[CourseResponse]:
    """Partial update course (admin only)."""
    if not check_resource_access(current_user.user_id, current_user.role):
        raise AuthorizationError("Access denied: only administrators can modify courses")
    course = await course_management_service.update_course(db, course_id, request)
    return SingleResponse(data=CourseResponse.model_validate(course))


@router.delete("/{course_id}", response_model=APIResponse[None])
async def delete_course(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("course:delete"))],
    course_id: int,
) -> APIResponse[None]:
    """Delete course (admin only)."""
    if not check_resource_access(current_user.user_id, current_user.role):
        raise AuthorizationError("Access denied: only administrators can delete courses")
    await course_management_service.delete_course(db, course_id)
    return APIResponse(data=None)
