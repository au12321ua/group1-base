"""Auth Service public endpoints (/auth/*)."""

from fastapi import APIRouter, Request

from auth_service.api.deps import AuthDbSession
from auth_service.deps import CurrentUserId
from auth_service.schemas.auth_schema import (
    ChangePasswordRequest,
    JwksResponse,
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
from auth_service.services.key_service import key_service
from shared.response import APIResponse

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    body: LoginRequest,
    http_request: Request,
    db: AuthDbSession,
) -> APIResponse[LoginResponse]:
    """User login — returns access + refresh token pair."""
    client_ip = http_request.client.host if http_request.client else ""
    data = await auth_service.login(
        db, body.username, body.password, client_ip=client_ip
    )
    return APIResponse(data=data)


@router.post("/sys/login", response_model=APIResponse[ServiceLoginResponse])
async def service_login(
    request: ServiceLoginRequest,
    db: AuthDbSession,
) -> APIResponse[ServiceLoginResponse]:
    """Service-to-service login — returns service token."""
    data = await auth_service.service_login(db, request.client_id, request.client_secret)
    return APIResponse(data=data)


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    request: LogoutRequest,
    db: AuthDbSession,
) -> APIResponse[None]:
    """Logout — revoke refresh token."""
    await auth_service.logout(db, request.refresh_token)
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
) -> APIResponse[None]:
    """Change password — requires old password verification."""
    await auth_service.change_password(db, current_user_id, request)
    return APIResponse(data=None)


@router.get("/public-key", response_model=APIResponse[JwksResponse])
async def get_public_keys() -> APIResponse[JwksResponse]:
    """Return JWKS public key set (no auth required)."""
    return APIResponse(data=key_service.get_public_keys())
