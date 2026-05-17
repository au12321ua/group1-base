"""Unified API response format."""

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    page_size: int


class APIResponse[T](BaseModel):
    """Standard API response wrapper.

    Success:
        {"code": 0, "message": "success", "data": {...}}
    Error:
        {"code": 1001, "message": "Authentication failed", "errors": [...]}
    """

    code: int = 0
    message: str = "success"
    data: T | None = None
    errors: list[dict[str, str]] | None = None


class PaginatedData[T](BaseModel):
    """Wraps list data with pagination info."""

    items: list[T]
    pagination: PaginationMeta


class ListResponse[T](APIResponse[PaginatedData[T]]):
    """Response wrapper for paginated list endpoints."""

    pass


class SingleResponse[T](APIResponse[T]):
    """Response wrapper for single-item endpoints."""

    pass
