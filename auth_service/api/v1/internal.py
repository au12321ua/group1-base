"""Auth Service internal endpoints (/internal/*) — only reachable within internal network."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response

from auth_service.api.deps import AuthDbSession
from auth_service.deps import ServiceTokenPayload
from auth_service.schemas.auth_schema import (
    InternalCreateUserRequest,
    InternalRoleSyncResponse,
    InternalSyncRolesRequest,
    InternalUserResponse,
    InternalVerifyRequest,
    InternalVerifyResponse,
)
from auth_service.services.auth_service import auth_service
from auth_service.services.identity_service import identity_service
from shared.response import APIResponse

router = APIRouter(tags=["internal"])


@router.post("/verify", response_model=APIResponse[InternalVerifyResponse])
async def verify_token(
    request: InternalVerifyRequest,
    db: AuthDbSession,
    _token: ServiceTokenPayload,
) -> APIResponse[InternalVerifyResponse]:
    """Verify JWT and return identity info (called by Gateway)."""
    data = await identity_service.verify_token(db, request)
    return APIResponse(data=data)


@router.post(
    "/users",
    status_code=201,
    response_model=APIResponse[InternalUserResponse],
)
async def create_internal_user(
    request: InternalCreateUserRequest,
    db: AuthDbSession,
    _token: ServiceTokenPayload,
) -> APIResponse[InternalUserResponse]:
    """Create minimal auth user + credential (called by Info Service on user creation)."""
    data = await auth_service.create_internal_user(
        db, request.user_id, request.username, request.role_ids
    )
    return APIResponse(data=data)


@router.post("/users/{user_id}/disable", response_model=APIResponse[None])
async def disable_user(
    user_id: str,
    db: AuthDbSession,
    _token: ServiceTokenPayload,
) -> APIResponse[None]:
    """Disable a user account (called by Info Service on logical delete)."""
    await auth_service.disable_user(db, user_id)
    return APIResponse(data=None)


@router.post("/users/{user_id}/enable", response_model=APIResponse[None])
async def enable_user(
    user_id: str,
    db: AuthDbSession,
    _token: ServiceTokenPayload,
) -> APIResponse[None]:
    """Enable a user account (called by Info Service on restore)."""
    await auth_service.enable_user(db, user_id)
    return APIResponse(data=None)


@router.post("/users/{user_id}/roles", response_model=APIResponse[InternalRoleSyncResponse])
async def sync_user_roles(
    user_id: str,
    request: InternalSyncRolesRequest,
    db: AuthDbSession,
    _token: ServiceTokenPayload,
) -> APIResponse[InternalRoleSyncResponse]:
    """Sync user role assignments (called by Info Service on role change)."""
    role_ids = await auth_service.sync_user_roles(db, user_id, request.role_ids)
    data = InternalRoleSyncResponse(
        user_id=user_id,
        role_ids=role_ids,
        synced_at=datetime.now(UTC),
    )
    return APIResponse(data=data)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AuthDbSession,
    _token: ServiceTokenPayload,
) -> Response:
    """Physically delete all auth data for a user (called by Info Service on permanent delete)."""
    await auth_service.delete_user(db, user_id)
    return Response(status_code=204)
