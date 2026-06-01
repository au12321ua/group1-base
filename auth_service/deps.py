"""FastAPI dependencies for Auth Service routes."""

from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth_service.core.security import verify_token
from shared.exceptions import AuthenticationError

_bearer = HTTPBearer(auto_error=False)

BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]


async def get_current_user_id(credentials: BearerCredentials) -> str:
    """从 Bearer Access Token 解析当前用户 ID。"""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError(message="Missing access token")
    payload = verify_token(credentials.credentials)
    if payload.get("type") != "access":
        raise AuthenticationError(message="Invalid token type")
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        raise AuthenticationError(message="Invalid token subject")
    return sub


CurrentUserId = Annotated[str, Depends(get_current_user_id)]


async def verify_service_token(credentials: BearerCredentials) -> dict[str, Any]:
    """验证 Service Token（用于内部服务间调用）。

    返回解码后的 JWT payload。仅接受 type == "service" 的令牌。
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError(message="Missing service token")
    payload = verify_token(credentials.credentials)
    if payload.get("type") != "service":
        raise AuthenticationError(message="Invalid token type: service token required")
    return payload


ServiceTokenPayload = Annotated[dict[str, Any], Depends(verify_service_token)]
