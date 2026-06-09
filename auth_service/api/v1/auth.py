"""Auth Service public endpoints (/auth/*)."""

from fastapi import APIRouter, Request

from auth_service.api.deps import AuditDbSession, AuthDbSession
from auth_service.core.security import verify_token
from auth_service.deps import CurrentUserId
from auth_service.schemas.auth_schema import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ServiceLoginRequest,
    ServiceLoginResponse,
)
from auth_service.schemas.user_schema import AuthUserResponse
from auth_service.services.auth_service import auth_service
from shared.exceptions import AccountDisabledError, AccountLockedError, AuthenticationError
from shared.response import APIResponse
from shared.services.audit_service import audit_service

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    body: LoginRequest,
    http_request: Request,
    db: AuthDbSession,
    audit_db: AuditDbSession,
) -> APIResponse[LoginResponse]:
    """User login — returns access + refresh token pair."""
    client_ip = http_request.client.host if http_request.client else ""
    try:
        data = await auth_service.login(
            db, body.username, body.password, client_ip=client_ip
        )
    except (AuthenticationError, AccountLockedError, AccountDisabledError) as exc:
        await audit_service.write_audit_log(
            audit_db,
            operator_user_id=body.username,
            operator_role="",
            target_type="auth",
            action="user_login",
            result="failed",
            reason=str(exc.message),
        )
        raise

    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=data.user_id,
        operator_role=data.role,
        target_type="auth",
        target_id=data.user_id,
        action="user_login",
        result="success",
    )
    return APIResponse(data=data)


@router.post("/sys/login", response_model=APIResponse[ServiceLoginResponse])
async def service_login(
    request: ServiceLoginRequest,
    db: AuthDbSession,
    audit_db: AuditDbSession,
) -> APIResponse[ServiceLoginResponse]:
    """Service-to-service login — returns service token."""
    try:
        data = await auth_service.service_login(db, request.client_id, request.client_secret)
    except AuthenticationError as exc:
        await audit_service.write_audit_log(
            audit_db,
            operator_user_id=request.client_id,
            operator_role="SERVICE",
            target_type="auth",
            action="service_login",
            result="failed",
            reason=str(exc.message),
        )
        raise

    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=request.client_id,
        operator_role="SERVICE",
        target_type="auth",
        action="service_login",
        result="success",
    )
    return APIResponse(data=data)


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    request: LogoutRequest,
    db: AuthDbSession,
    audit_db: AuditDbSession,
) -> APIResponse[None]:
    """Logout — revoke refresh token."""
    # Extract user_id from refresh token for audit before revocation
    try:
        payload = verify_token(request.refresh_token)
        user_id = payload.get("sub", "")
    except Exception:
        user_id = ""

    await auth_service.logout(db, request.refresh_token)

    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=user_id,
        operator_role="",
        target_type="auth",
        action="user_logout",
        result="success",
    )
    return APIResponse(data=None)


@router.post("/refresh", response_model=APIResponse[RefreshTokenResponse])
async def refresh_token(
    request: RefreshTokenRequest,
    db: AuthDbSession,
) -> APIResponse[RefreshTokenResponse]:
    """Refresh token pair — rotate both access and refresh tokens."""
    data = await auth_service.refresh_token(db, request.refresh_token)
    return APIResponse(data=data)


@router.get("/me", response_model=APIResponse[AuthUserResponse])
async def get_current_user(
    current_user_id: CurrentUserId,
    db: AuthDbSession,
) -> APIResponse[AuthUserResponse]:
    """Get current authenticated user info."""
    data = await auth_service.get_current_user(db, current_user_id)
    return APIResponse(data=data)


@router.post("/change-password", response_model=APIResponse[None])
async def change_password(
    request: ChangePasswordRequest,
    current_user_id: CurrentUserId,
    db: AuthDbSession,
    audit_db: AuditDbSession,
) -> APIResponse[None]:
    """Change password — requires old password verification."""
    await auth_service.change_password(db, current_user_id, request)

    await audit_service.write_audit_log(
        audit_db,
        operator_user_id=current_user_id,
        operator_role="",
        target_type="auth",
        target_id=current_user_id,
        action="password_changed",
        result="success",
    )
    return APIResponse(data=None)
