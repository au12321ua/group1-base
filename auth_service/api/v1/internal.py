"""Auth Service internal endpoints (/internal/*) — only reachable within internal network."""

import warnings

from fastapi import APIRouter

from auth_service.schemas.auth_schema import (
    InternalCreateUserRequest,
    InternalRoleSyncResponse,
    InternalSyncRolesRequest,
    InternalUserResponse,
    InternalVerifyRequest,
    InternalVerifyResponse,
)
from shared.response import APIResponse

router = APIRouter(tags=["internal"])


@router.post("/verify", response_model=APIResponse[InternalVerifyResponse])
async def verify_token(request: InternalVerifyRequest) -> APIResponse[InternalVerifyResponse]:
    """Verify JWT and return identity info (called by Gateway)."""
    warnings.warn("TODO: implement POST /internal/verify")
    raise NotImplementedError("POST /internal/verify not implemented")


@router.post("/users", response_model=APIResponse[InternalUserResponse])
async def create_internal_user(
    request: InternalCreateUserRequest,
) -> APIResponse[InternalUserResponse]:
    """Create minimal auth user + credential (called by Info Service on user creation)."""
    warnings.warn("TODO: implement POST /internal/users")
    raise NotImplementedError("POST /internal/users not implemented")


@router.post("/users/{user_id}/disable", response_model=APIResponse[None])
async def disable_user(user_id: str) -> APIResponse[None]:
    """Disable a user account (called by Info Service on logical delete)."""
    warnings.warn("TODO: implement POST /internal/users/{id}/disable")
    raise NotImplementedError("POST /internal/users/{id}/disable not implemented")


@router.post("/users/{user_id}/enable", response_model=APIResponse[None])
async def enable_user(user_id: str) -> APIResponse[None]:
    """Enable a user account (called by Info Service on restore)."""
    warnings.warn("TODO: implement POST /internal/users/{id}/enable")
    raise NotImplementedError("POST /internal/users/{id}/enable not implemented")


@router.post("/users/{user_id}/roles", response_model=APIResponse[InternalRoleSyncResponse])
async def sync_user_roles(
    user_id: str, request: InternalSyncRolesRequest
) -> APIResponse[InternalRoleSyncResponse]:
    """Sync user role assignments (called by Info Service on role change)."""
    warnings.warn("TODO: implement POST /internal/users/{id}/roles")
    raise NotImplementedError("POST /internal/users/{id}/roles not implemented")


@router.delete("/users/{user_id}", response_model=APIResponse[None])
async def delete_user(user_id: str) -> APIResponse[None]:
    """Physically delete all auth data for a user (called by Info Service on permanent delete)."""
    warnings.warn("TODO: implement DELETE /internal/users/{id}")
    raise NotImplementedError("DELETE /internal/users/{id} not implemented")
