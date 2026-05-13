"""IdentityService — token verification and identity extraction (for Gateway)."""

import warnings

from auth_service.schemas.auth_schema import InternalVerifyRequest, InternalVerifyResponse


class IdentityService:
    """Verifies JWT tokens and extracts identity for Gateway.

    Called by Gateway via POST /internal/verify.
    Returns user_id, username, role, permissions that Gateway
    then forwards as HTTP headers to downstream services.
    """

    def __init__(self) -> None:
        warnings.warn("TODO: IdentityService — implement all methods")

    async def verify_token(self, request: InternalVerifyRequest) -> InternalVerifyResponse:
        """Verify a JWT (access or service token) and return identity info.

        Steps:
        1. Decode and verify JWT signature (HS256)
        2. Check token type (access/service)
        3. Check expiry
        4. For access tokens: look up user roles/permissions from DB
        5. For service tokens: extract scope from payload
        """
        warnings.warn("TODO: implement verify_token — JWT decode + identity extraction")
        raise NotImplementedError("verify_token not implemented")


identity_service = IdentityService()
