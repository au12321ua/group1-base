"""Shared utilities for Auth Service and Info Service."""

from shared.database import create_get_db
from shared.error_handlers import register_error_handlers

__all__ = ["create_get_db", "register_error_handlers"]
