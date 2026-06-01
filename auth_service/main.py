"""Auth Service — FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

import auth_service.models  # noqa: F401  — register tables in SQLModel.metadata
import shared.models.audit_log  # noqa: F401  — register audit tables in SQLModel.metadata
from auth_service.api.v1.router import router as v1_router
from auth_service.core.config import get_auth_settings
from shared.database import create_get_db
from shared.error_handlers import register_error_handlers
from shared.logging import RequestIDMiddleware, RequestLoggingMiddleware, get_logger

settings = get_auth_settings()
engine = create_async_engine(settings.auth_database_url, echo=False)
audit_engine = create_async_engine(settings.audit_database_url, echo=False)
get_db = create_get_db(engine)
get_audit_db = create_get_db(audit_engine)

__all__ = ["app", "engine", "get_db", "audit_engine", "get_audit_db"]

_AUTH_TABLES = frozenset(
    {
        "users",
        "credentials",
        "roles",
        "user_roles",
        "permissions",
        "role_permissions",
        "tokens",
        "authentication_sessions",
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
    """Create Auth + Audit DB tables and runtime dirs on startup, dispose engines on shutdown."""
    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(_create_tables, _AUTH_TABLES)
    async with audit_engine.begin() as conn:
        await conn.run_sync(_create_tables, _AUDIT_TABLES)
    yield
    await engine.dispose()
    await audit_engine.dispose()


app = FastAPI(
    title="STSS Auth Service",
    version="0.1.0",
    description="Authentication and authorization for STSS",
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
    logger=get_logger("auth_service.request", service_name="auth_service"),
)

register_error_handlers(app)
app.include_router(v1_router, prefix="/api/v1")
