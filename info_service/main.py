"""Info Service — FastAPI application entry point."""

import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

warnings.warn("TODO: complete main.py — DB init, router registration, lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — DB connect/disconnect."""
    warnings.warn("TODO: implement lifespan — database connection management")
    yield


app = FastAPI(
    title="STSS Info Service",
    version="0.1.0",
    description="Business data management for STSS (Info Management)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: include routers
# from info_service.api.v1.router import router as v1_router
# app.include_router(v1_router, prefix="/api/v1")
