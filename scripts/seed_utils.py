"""Seed script utilities: idempotent checks, logging, sync engine creation."""

from sqlalchemy import Engine, create_engine, text
from sqlmodel import SQLModel


def make_sync_url(async_url: str) -> str:
    """Convert an async SQLAlchemy URL to its sync equivalent.

    >>> make_sync_url("sqlite+aiosqlite:///./data/auth.db")
    'sqlite:///./data/auth.db'
    """
    return async_url.replace("+aiosqlite", "")


def create_sync_engine(database_url: str) -> Engine:
    """Create a synchronous SQLAlchemy engine from an async-compatible URL."""
    return create_engine(make_sync_url(database_url), echo=False)


def is_table_empty(engine: Engine, table_name: str) -> bool:
    """Return True if the given table has zero rows."""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        return count == 0


def print_step(message: str) -> None:
    """Print a formatted step message."""
    print(f"  {message}")


def print_header(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def clear_all_tables(engine: Engine) -> None:
    """Drop and recreate all registered SQLModel tables."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print_step("已清空所有表并重建")
