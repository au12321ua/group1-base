"""Info Service — /users/* endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from info_service.api.deps import AuditDbSession, InfoDbSession
from info_service.core.security import check_resource_access
from info_service.deps import require_permission
from info_service.schemas.user_schema import (
    UserCreateRequest,
    UserImportResult,
    UserListQuery,
    UserPatchRequest,
    UserResponse,
    UserUpdateRequest,
)
from info_service.services.audit_service import audit_service
from info_service.services.user_management_service import user_management_service
from shared.exceptions import AuthorizationError
from shared.response import APIResponse, PaginatedData, PaginationMeta
from shared.security import IdentityContext

router = APIRouter(tags=["users"])


@router.get("/", response_model=APIResponse[PaginatedData[UserResponse]])
async def list_users(
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:read"))],
    query: Annotated[UserListQuery, Depends()],
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
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:create"))],
) -> APIResponse[UserResponse]:
    """Create a new user (cross-service sync with Auth Service)."""
    user = await user_management_service.create_user(db, request, current_user)
    # Audit log
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user.user_id,
        operator_role=current_user.role,
        target_type="user",
        target_id=str(user.id),
        action="user_created",
        result="success",
        request_id=current_user.request_id,
    )
    return APIResponse(data=user)


@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: int,
    db: InfoDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:read"))],
) -> APIResponse[UserResponse]:
    """Get user detail with profile (own profile or admin only)."""
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_owner_id=str(user_id),
    ):
        raise AuthorizationError("Access denied: can only view own profile")
    user = await user_management_service.get_user(db, user_id)
    return APIResponse(data=user)


@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:update"))],
) -> APIResponse[UserResponse]:
    """Full update user (own profile or admin only)."""
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_owner_id=str(user_id),
    ):
        raise AuthorizationError("Access denied: can only update own profile")
    # Check if role changed
    old_user = await user_management_service.get_user(db, user_id)
    old_roles = old_user.role_ids

    user = await user_management_service.update_user(db, user_id, request, current_user)

    # Audit log for role change
    if user.role_ids != old_roles:
        await audit_service.write_audit_log(
            audit_db,
            operator_user_id=current_user.user_id,
            operator_role=current_user.role,
            target_type="user",
            target_id=str(user_id),
            action="role_changed",
            result="success",
            request_id=current_user.request_id,
        )
    return APIResponse(data=user)


@router.patch("/{user_id}", response_model=APIResponse[UserResponse])
async def patch_user(
    user_id: int,
    request: UserPatchRequest,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:update"))],
) -> APIResponse[UserResponse]:
    """Partial update user (own profile or admin only, may trigger role sync with Auth)."""
    if not check_resource_access(
        current_user.user_id, current_user.role,
        resource_owner_id=str(user_id),
    ):
        raise AuthorizationError("Access denied: can only update own profile")
    old_user = await user_management_service.get_user(db, user_id)
    old_roles = old_user.role_ids

    user = await user_management_service.patch_user(db, user_id, request, current_user)

    # Audit log for role change
    if user.role_ids != old_roles:
        await audit_service.write_audit_log(
            audit_db,
            operator_user_id=current_user.user_id,
            operator_role=current_user.role,
            target_type="user",
            target_id=str(user_id),
            action="role_changed",
            result="success",
            request_id=current_user.request_id,
        )
    return APIResponse(data=user)


@router.delete("/{user_id}", response_model=APIResponse[None])
async def delete_user(
    user_id: int,
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:delete"))],
) -> APIResponse[None]:
    """Logical delete user → recycle bin (admin only)."""
    if not check_resource_access(current_user.user_id, current_user.role):
        raise AuthorizationError("Access denied: only administrators can delete users")
    await user_management_service.logical_delete_user(db, user_id, current_user)
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user.user_id,
        operator_role=current_user.role,
        target_type="user",
        target_id=str(user_id),
        action="user_deleted_logical",
        result="success",
        request_id=current_user.request_id,
    )
    return APIResponse(data=None)


@router.post("/import", response_model=APIResponse[UserImportResult])
async def batch_import_users(
    db: InfoDbSession,
    audit_db: AuditDbSession,
    current_user: Annotated[IdentityContext, Depends(require_permission("user:create"))],
    file: UploadFile = File(...),
) -> APIResponse[UserImportResult]:
    """CSV batch import users."""
    content = await file.read()
    result = await user_management_service.batch_import_users(db, content)
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user.user_id,
        operator_role=current_user.role,
        target_type="user",
        action="user_batch_imported",
        result="success" if result.failed_count == 0 else "partial",
        reason=(
            f"total={result.total}, success={result.success_count}, "
            f"failed={result.failed_count}"
        ),
        request_id=current_user.request_id,
    )
    return APIResponse(data=result)
