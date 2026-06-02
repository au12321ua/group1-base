"""Shared Auth Service HTTP client helpers.

Centralises cross-service HTTP calls to Auth Service so that individual
Info Service modules don't duplicate httpx boilerplate.
"""

import logging

import httpx

from info_service.core.config import InfoSettings

logger = logging.getLogger(__name__)


async def batch_fetch_role_names(
    settings: InfoSettings, user_ids: list[int]
) -> dict[int, list[str]]:
    """POST /internal/users/roles/batch — get role_names for multiple users.

    Returns {user_id: [role_name, ...]} mapping.
    Returns an empty dict on any error (best-effort enrichment).
    """
    if not user_ids:
        return {}
    try:
        async with httpx.AsyncClient(timeout=settings.auth_service_timeout) as client:
            resp = await client.post(
                f"{settings.auth_service_url}/api/v1/internal/users/roles/batch",
                json={"user_ids": [str(uid) for uid in user_ids]},
            )
            if resp.status_code == 200:
                data = resp.json()
                users = data.get("data", {}).get("users", [])
                return {
                    int(u["user_id"]): u.get("role_names", [])
                    for u in users
                }
    except Exception:
        logger.exception("Failed to batch fetch roles from Auth")
    return {}
