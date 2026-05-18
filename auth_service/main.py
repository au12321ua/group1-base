"""Auth Service — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

import auth_service.models  # noqa: F401  — register tables in SQLModel.metadata
from auth_service.api.v1.router import router as v1_router
from auth_service.core.config import get_auth_settings
from shared.database import create_get_db
from shared.error_handlers import register_error_handlers

settings = get_auth_settings()
engine = create_async_engine(settings.auth_database_url, echo=False)
get_db = create_get_db(engine)

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create Auth DB tables on startup, dispose engine on shutdown."""
    async with engine.begin() as conn:
        tables = [t for t in SQLModel.metadata.sorted_tables if t.name in _AUTH_TABLES]
        await conn.run_sync(SQLModel.metadata.create_all, tables=tables)
    yield
    await engine.dispose()


app = FastAPI(
    title="STSS Auth Service",
    version="0.1.0",
    description="Authentication and authorization for STSS",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(v1_router, prefix="/api/v1")
