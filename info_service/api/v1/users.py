"""Info Service — /users/* endpoints."""

from fastapi import APIRouter, Depends, File, UploadFile

from info_service.api.deps import InfoDbSession
from info_service.deps import require_permission
from info_service.schemas.user_schema import (
    UserCreateRequest,
    UserImportResult,
    UserListQuery,
    UserPatchRequest,
    UserResponse,
    UserUpdateRequest,
)
from info_service.services.user_management_service import user_management_service
from shared.response import APIResponse, PaginatedData, PaginationMeta
from shared.security import IdentityContext

router = APIRouter(tags=["users"])


@router.get("/", response_model=APIResponse[PaginatedData[UserResponse]])
async def list_users(
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:read")),
    query: UserListQuery = Depends(),
) -> APIResponse[PaginatedData[UserResponse]]:
    """Get paginated user list with filters."""
    items, total = await user_management_service.list_users(
        db,
        page=query.page,
        page_size=query.page_size,
        keyword=query.keyword,
        status=query.status,
        role=query.role,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
    )
    return APIResponse(
        data=PaginatedData(
            items=items,
            pagination=PaginationMeta(
                total=total, page=query.page, page_size=query.page_size
            ),
        )
    )


@router.post("/", status_code=201, response_model=APIResponse[UserResponse])
async def create_user(
    request: UserCreateRequest,
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:create")),
) -> APIResponse[UserResponse]:
    """Create a new user (cross-service sync with Auth Service)."""
    user = await user_management_service.create_user(db, request, current_user)
    return APIResponse(data=user)


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:read")),
) -> APIResponse[UserResponse]:
    """Get user detail with profile."""
    user = await user_management_service.get_user(db, user_id)
    return APIResponse(data=user)


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:update")),
) -> APIResponse[UserResponse]:
    """Full update user."""
    user = await user_management_service.update_user(db, user_id, request, current_user)
    return APIResponse(data=user)


@router.patch("/{user_id}", response_model=APIResponse[UserResponse])
async def patch_user(
    user_id: int,
    request: UserPatchRequest,
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:update")),
) -> APIResponse[UserResponse]:
    """Partial update user (may trigger role sync with Auth)."""
    user = await user_management_service.patch_user(db, user_id, request, current_user)
    return APIResponse(data=user)


@router.delete("/{user_id}", response_model=APIResponse[None])
async def delete_user(
    user_id: int,
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:delete")),
) -> APIResponse[None]:
    """Logical delete user → recycle bin."""
    await user_management_service.logical_delete_user(db, user_id, current_user)
    return APIResponse(data=None)


@router.post("/import", response_model=APIResponse[UserImportResult])
async def batch_import_users(
    db: InfoDbSession,
    current_user: IdentityContext = Depends(require_permission("user:create")),
    file: UploadFile = File(...),
) -> APIResponse[UserImportResult]:
    """CSV batch import users."""
    content = await file.read()
    result = await user_management_service.batch_import_users(db, content)
    return APIResponse(data=result)
