"""Auth Service public endpoints (/auth/*)."""

import warnings

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

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
from shared.response import APIResponse

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(request: LoginRequest) -> APIResponse[LoginResponse]:
    """User login — returns access + refresh token pair."""
    warnings.warn("TODO: implement POST /auth/login")
    raise NotImplementedError("POST /auth/login not implemented")


@router.post("/sys/login", response_model=APIResponse[ServiceLoginResponse])
async def service_login(request: ServiceLoginRequest) -> APIResponse[ServiceLoginResponse]:
    """Service-to-service login — returns service token."""
    warnings.warn("TODO: implement POST /auth/sys/login")
    raise NotImplementedError("POST /auth/sys/login not implemented")


@router.post("/logout", response_model=APIResponse[None])
async def logout(request: LogoutRequest) -> APIResponse[None]:
    """Logout — revoke refresh token."""
    warnings.warn("TODO: implement POST /auth/logout")
    raise NotImplementedError("POST /auth/logout not implemented")


@router.post("/refresh", response_model=APIResponse[RefreshTokenResponse])
async def refresh_token(request: RefreshTokenRequest) -> APIResponse[RefreshTokenResponse]:
    """Refresh token pair — rotate both access and refresh tokens."""
    warnings.warn("TODO: implement POST /auth/refresh")
    raise NotImplementedError("POST /auth/refresh not implemented")


@router.get("/me", response_model=APIResponse[AuthUserResponse])
async def get_current_user() -> APIResponse[AuthUserResponse]:
    """Get current authenticated user info."""
    warnings.warn("TODO: implement GET /auth/me")
    raise NotImplementedError("GET /auth/me not implemented")


@router.post("/change-password", response_model=APIResponse[None])
async def change_password(request: ChangePasswordRequest) -> APIResponse[None]:
    """Change password — requires old password verification."""
    warnings.warn("TODO: implement POST /auth/change-password")
    raise NotImplementedError("POST /auth/change-password not implemented")


@router.get("/public-key")
async def get_public_keys() -> dict:
    """Return JWKS public key set (no auth required)."""
    warnings.warn("TODO: implement GET /auth/public-key")
    raise NotImplementedError("GET /auth/public-key not implemented")
