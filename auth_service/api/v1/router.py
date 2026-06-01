"""Auth Service v1 router — aggregates all sub-routers."""

from fastapi import APIRouter

from auth_service.api.v1.auth import router as auth_router
from auth_service.api.v1.internal import router as internal_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(internal_router, prefix="/internal", tags=["internal"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint for Docker / orchestration."""
    return {"status": "ok"}
