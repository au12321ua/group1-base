"""Info Service — /offerings/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from info_service.api.deps import InfoDbSession
from info_service.core.security import check_resource_access
from info_service.deps import require_permission
from info_service.models.course_offering import CourseOffering
from info_service.schemas.offering_schema import (
    OfferingCreateRequest,
    OfferingPatchRequest,
    OfferingResponse,
    OfferingUpdateRequest,
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

router = APIRouter(tags=["offerings"])


async def _check_offering_access(
    current_user: IdentityContext, db, offering_id: int,
) -> CourseOffering:
    """Verify the current user can modify the offering, returning it for reuse."""
    offering = await course_management_service.get_offering(db, offering_id)
    teacher_ids = [t for t in offering.teacher_ids.split(",") if t]
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_teacher_ids=teacher_ids,
    ):
        raise AuthorizationError(
            "Access denied: only assigned teachers or administrators can modify this offering"
        )
    return offering


@router.get("/", response_model=ListResponse[OfferingResponse])
async def list_offerings(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:read"))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    course_id: int | None = Query(default=None),
    term_code: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> ListResponse[OfferingResponse]:
    """Get paginated offering list."""
    skip = (page - 1) * page_size
    items, total = await course_management_service.list_offerings(
        db,
        skip=skip,
        limit=page_size,
        course_id=course_id,
        term_code=term_code,
        status=status,
    )
    return ListResponse(
        data=PaginatedData(
            items=[OfferingResponse.model_validate(item) for item in items],
            pagination=PaginationMeta(total=total, page=page, page_size=page_size),
        )
    )


@router.post("/", response_model=SingleResponse[OfferingResponse])
async def create_offering(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:create"))],
    request: OfferingCreateRequest,
) -> SingleResponse[OfferingResponse]:
    """Create a new offering."""
    offering = await course_management_service.create_offering(db, request)
    return SingleResponse(data=OfferingResponse.model_validate(offering))


@router.get("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def get_offering(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:read"))],
    offering_id: int,
) -> SingleResponse[OfferingResponse]:
    """Get offering detail."""
    offering = await course_management_service.get_offering(db, offering_id)
    return SingleResponse(data=OfferingResponse.model_validate(offering))


@router.put("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def update_offering(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:update"))],
    offering_id: int,
    request: OfferingUpdateRequest,
) -> SingleResponse[OfferingResponse]:
    """Full update offering (assigned teachers or admin only)."""
    await _check_offering_access(current_user, db, offering_id)
    offering = await course_management_service.update_offering(db, offering_id, request)
    return SingleResponse(data=OfferingResponse.model_validate(offering))


@router.patch("/{offering_id}", response_model=SingleResponse[OfferingResponse])
async def patch_offering(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:update"))],
    offering_id: int,
    request: OfferingPatchRequest,
) -> SingleResponse[OfferingResponse]:
    """Partial update offering (assigned teachers or admin only)."""
    await _check_offering_access(current_user, db, offering_id)
    offering = await course_management_service.update_offering(db, offering_id, request)
    return SingleResponse(data=OfferingResponse.model_validate(offering))


@router.delete("/{offering_id}", response_model=APIResponse[None])
async def delete_offering(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("offering:delete"))],
    offering_id: int,
) -> APIResponse[None]:
    """Delete offering (assigned teachers or admin only)."""
    await _check_offering_access(current_user, db, offering_id)
    await course_management_service.delete_offering(db, offering_id)
    return APIResponse(data=None)
