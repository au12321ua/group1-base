"""Auth Service v1 router — aggregates all sub-routers."""

import warnings

from fastapi import APIRouter

warnings.warn("TODO: import and include auth and internal sub-routers")

router = APIRouter()

# router.include_router(auth_router, prefix="/auth", tags=["auth"])
# router.include_router(internal_router, prefix="/internal", tags=["internal"])
