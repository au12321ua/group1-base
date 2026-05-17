"""Auth-related request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    role: str


class ServiceLoginRequest(BaseModel):
    client_id: str = Field(..., min_length=1)
    client_secret: str = Field(..., min_length=1)


class ServiceLoginResponse(BaseModel):
    service_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


# ---- JWKS / Public Key ----


class JwksKey(BaseModel):
    kty: str = "oct"
    use: str = "sig"
    alg: str = "HS256"
    kid: str


class JwksResponse(BaseModel):
    keys: list[JwksKey]


# ---- Internal endpoint schemas ----


class InternalCreateUserRequest(BaseModel):
    user_id: str
    username: str
    role_ids: list[int] = Field(default_factory=list)


class InternalUserResponse(BaseModel):
    user_id: str
    username: str
    status: str


class InternalVerifyRequest(BaseModel):
    token: str = Field(..., min_length=1)


class InternalVerifyResponse(BaseModel):
    user_id: str
    username: str
    role: str
    permissions: list[str]
    token_type: str


class InternalSyncRolesRequest(BaseModel):
    role_ids: list[int]


class InternalRoleSyncResponse(BaseModel):
    user_id: str
    role_ids: list[int]
    synced_at: datetime
