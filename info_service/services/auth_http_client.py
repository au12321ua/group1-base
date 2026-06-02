"""Info Service HTTP client for Auth Service internal endpoints.

Manages the full service token lifecycle:
- Acquire token from /auth/sys/login on first use
- Cache token in memory
- Auto-refresh at 80% of expiry window
- Attach Authorization: Bearer <token> to every request
"""

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AuthServiceClient:
    """HTTP client for cross-service calls to Auth Service internal endpoints."""

    LOGIN_PATH = "/api/v1/auth/sys/login"
    INTERNAL_PREFIX = "/api/v1/internal"

    def __init__(
        self,
        auth_service_url: str,
        client_id: str,
        client_secret: str,
        timeout: int = 10,
    ) -> None:
        self._base_url = auth_service_url.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._timeout = timeout
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    # ------------------------------------------------------------------
    # Token lifecycle
    # ------------------------------------------------------------------

    async def _acquire_token(self) -> str:
        """POST /auth/sys/login and return the service token string."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}{self.LOGIN_PATH}",
                json={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            resp.raise_for_status()
            payload = resp.json()
            data = payload.get("data", payload)
            token = data["service_token"]
            # Refresh at 80% of expiry to avoid race conditions
            expires_in = data.get("expires_in", 28800)
            self._token_expires_at = time.time() + expires_in * 0.8
            logger.info("Acquired new service token, expires_in=%s", expires_in)
            return token

    async def _get_token(self) -> str:
        """Return a cached token, refreshing if expired or absent."""
        if self._token is None or time.time() >= self._token_expires_at:
            self._token = await self._acquire_token()
        return self._token

    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> httpx.Response:
        """Send an HTTP request with an Authorization header attached."""
        token = await self._get_token()
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", f"Bearer {token}")
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await client.request(
                method,
                f"{self._base_url}{path}",
                headers=headers,
                **kwargs,
            )

    async def post_internal(self, path: str, **kwargs: Any) -> httpx.Response:
        """POST to an Auth Service internal endpoint (prefix auto-prepended)."""
        full_path = f"{self.INTERNAL_PREFIX}{path}"
        return await self._request("POST", full_path, **kwargs)

    async def delete_internal(self, path: str, **kwargs: Any) -> httpx.Response:
        """DELETE to an Auth Service internal endpoint (prefix auto-prepended)."""
        full_path = f"{self.INTERNAL_PREFIX}{path}"
        return await self._request("DELETE", full_path, **kwargs)


# ------------------------------------------------------------------
# Module-level singleton (lazy init, same pattern as service singletons)
# ------------------------------------------------------------------

_auth_client: AuthServiceClient | None = None


def get_auth_service_client() -> AuthServiceClient:
    """Return the module-level singleton AuthServiceClient, creating it on first call."""
    global _auth_client
    if _auth_client is None:
        from info_service.core.config import get_info_settings

        settings = get_info_settings()
        _auth_client = AuthServiceClient(
            auth_service_url=settings.auth_service_url,
            client_id=settings.auth_service_client_id,
            client_secret=settings.auth_service_client_secret,
            timeout=settings.auth_service_timeout,
        )
    return _auth_client
