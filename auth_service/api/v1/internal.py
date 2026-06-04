"""Auth Service internal endpoints (/internal/*) — only reachable within internal network."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from auth_service.api.deps import AuditDbSession, AuthDbSession
from auth_service.deps import ServiceTokenPayload
from auth_service.schemas.auth_schema import (
    InternalBatchRolesRequest,
    InternalBatchRolesResponse,
    InternalCreateUserRequest,
    InternalRoleSyncResponse,
    InternalSyncRolesRequest,
    InternalUserResponse,
    InternalUserRoleItem,
    InternalVerifyRequest,
    InternalVerifyResponse,
)
from auth_service.services.auth_service import auth_service
from auth_service.services.identity_service import identity_service
from shared.response import APIResponse
from shared.security import extract_service_operator
from shared.services.audit_service import audit_service

router = APIRouter(tags=["internal"])


async def _write_internal_audit(
    audit_db: AsyncSession,
    service_auth: dict,
    target_id: str,
    action: str,
    reason: str = "",
) -> None:
    """Write an audit log entry for a service-level internal operation."""
    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=extract_service_operator(service_auth),
        operator_role="SERVICE",
        target_type="user",
        target_id=target_id,
        action=action,
        result="success",
        reason=reason,
    )


@router.post("/verify", response_model=APIResponse[InternalVerifyResponse])
async def verify_token(
    request: InternalVerifyRequest,
    db: AuthDbSession,
    _service_auth: ServiceTokenPayload,  # guard: validates service token before endpoint runs
) -> JSONResponse:
    """Verify JWT and return identity info (called by Gateway).

    Also returns user identity in response headers (X-User-Id, X-User-Role,
    X-User-Permissions) so nginx can extract them via auth_request_set.
    """
    data = await identity_service.verify_token(db, request)
    permissions = (
        ",".join(data.permissions) if isinstance(data.permissions, list)
        else str(data.permissions) if data.permissions
        else ""
    )
    return JSONResponse(
        content=APIResponse(data=data).model_dump(),
        headers={
            "X-User-Id": str(data.user_id) if data.user_id else "",
            "X-User-Role": str(data.role) if data.role else "",
            "X-User-Permissions": permissions,
        },
    )


@router.post(
    "/users",
    status_code=201,
    response_model=APIResponse[InternalUserResponse],
)
async def create_internal_user(
    request: InternalCreateUserRequest,
    db: AuthDbSession,
    audit_db: AuditDbSession,
    _service_auth: ServiceTokenPayload,  # guard: validates service token before endpoint runs
) -> APIResponse[InternalUserResponse]:
    """Create minimal auth user + credential (called by Info Service on user creation)."""
    data = await auth_service.create_internal_user(
        db, request.user_id, request.username, request.role_ids
    )
    await _write_internal_audit(audit_db, _service_auth, request.user_id, "user_created")
    return APIResponse(data=data)


@router.post("/users/{user_id}/disable", response_model=APIResponse[None])
async def disable_user(
    user_id: str,
    db: AuthDbSession,
    audit_db: AuditDbSession,
    _service_auth: ServiceTokenPayload,  # guard: validates service token before endpoint runs
) -> APIResponse[None]:
    """Disable a user account (called by Info Service on logical delete)."""
    await auth_service.disable_user(db, user_id)
    await _write_internal_audit(audit_db, _service_auth, user_id, "user_disabled")
    return APIResponse(data=None)


@router.post("/users/{user_id}/enable", response_model=APIResponse[None])
async def enable_user(
    user_id: str,
    db: AuthDbSession,
    audit_db: AuditDbSession,
    _service_auth: ServiceTokenPayload,  # guard: validates service token before endpoint runs
) -> APIResponse[None]:
    """Enable a user account (called by Info Service on restore)."""
    await auth_service.enable_user(db, user_id)
    await _write_internal_audit(audit_db, _service_auth, user_id, "user_enabled")
    return APIResponse(data=None)


@router.post("/users/{user_id}/roles", response_model=APIResponse[InternalRoleSyncResponse])
async def sync_user_roles(
    user_id: str,
    request: InternalSyncRolesRequest,
    db: AuthDbSession,
    audit_db: AuditDbSession,
    _service_auth: ServiceTokenPayload,  # guard: validates service token before endpoint runs
) -> APIResponse[InternalRoleSyncResponse]:
    """Sync user role assignments (called by Info Service on role change)."""
    role_ids = await auth_service.sync_user_roles(db, user_id, request.role_ids)
    await _write_internal_audit(
        audit_db, _service_auth, user_id, "user_roles_synced", reason=f"roles: {role_ids}"
    )
    data = InternalRoleSyncResponse(
        user_id=user_id,
        role_ids=role_ids,
        synced_at=datetime.now(UTC),
    )
    return APIResponse(data=data)


@router.post("/users/roles/batch", response_model=APIResponse[InternalBatchRolesResponse])
async def batch_get_user_roles(
    request: InternalBatchRolesRequest,
    db: AuthDbSession,
    _service_auth: ServiceTokenPayload,
) -> APIResponse[InternalBatchRolesResponse]:
    """Batch query roles for multiple users (called by Info Service)."""
    role_map = await auth_service.batch_get_user_roles(db, request.user_ids)
    users = [
        InternalUserRoleItem(user_id=uid, role_codes=codes, role_names=names)
        for uid, (codes, names) in role_map.items()
    ]
    return APIResponse(data=InternalBatchRolesResponse(users=users))


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: AuthDbSession,
    audit_db: AuditDbSession,
    _service_auth: ServiceTokenPayload,  # guard: validates service token before endpoint runs
) -> Response:
    """Physically delete all auth data for a user (called by Info Service on permanent delete)."""
    await auth_service.delete_user(db, user_id)
    await _write_internal_audit(audit_db, _service_auth, user_id, "user_deleted")
    return Response(status_code=204)
