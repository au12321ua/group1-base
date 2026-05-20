"""Info Service — FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

import info_service.models  # noqa: F401  — register tables in SQLModel.metadata
from info_service.api.v1.router import router as v1_router
from info_service.core.config import get_info_settings
from shared.database import create_get_db
from shared.error_handlers import register_error_handlers
from shared.logging import RequestIDMiddleware, RequestLoggingMiddleware, get_logger

settings = get_info_settings()
info_engine = create_async_engine(settings.info_database_url, echo=False)
audit_engine = create_async_engine(settings.audit_database_url, echo=False)
get_info_db = create_get_db(info_engine)
get_audit_db = create_get_db(audit_engine)

_INFO_TABLES = frozenset(
    {
        "users_info",
        "user_profiles",
        "courses",
        "course_offerings",
        "course_prerequisites",
        "course_schedules",
        "teacher_course_assignments",
        "classrooms",
        "training_programs",
        "academic_calendars",
        "base_info_items",
        "file_resources",
    }
)

_AUDIT_TABLES = frozenset(
    {
        "audit_logs",
        "dead_letter_queue",
        "operation_logs",
    }
)


def _create_tables(conn, table_names: frozenset[str]) -> None:
    tables = [t for t in SQLModel.metadata.sorted_tables if t.name in table_names]
    SQLModel.metadata.create_all(conn, tables=tables)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create Info + Audit DB tables and runtime dirs on startup, dispose engines on shutdown."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs("data", exist_ok=True)
    async with info_engine.begin() as conn:
        await conn.run_sync(_create_tables, _INFO_TABLES)
    async with audit_engine.begin() as conn:
        await conn.run_sync(_create_tables, _AUDIT_TABLES)
    yield
    await info_engine.dispose()
    await audit_engine.dispose()


app = FastAPI(
    title="STSS Info Service",
    version="0.1.0",
    description="Business data management for STSS (Info Management)",
    lifespan=lifespan,
)

origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    RequestLoggingMiddleware,
    logger=get_logger("info_service.request", service_name="info_service"),
)

register_error_handlers(app)
app.include_router(v1_router, prefix="/api/v1")
