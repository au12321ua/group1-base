"""Unified API response format."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    page_size: int


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper.

    Success:
        {"code": 0, "message": "success", "data": {...}}
    Error:
        {"code": 1001, "message": "Authentication failed", "errors": [...]}
    """

    code: int = 0
    message: str = "success"
    data: Optional[T] = None
    errors: Optional[list[dict[str, str]]] = None


class PaginatedData(BaseModel, Generic[T]):
    """Wraps list data with pagination info."""

    items: list[T]
    pagination: PaginationMeta


class ListResponse(APIResponse[PaginatedData[T]], Generic[T]):
    """Response wrapper for paginated list endpoints."""

    pass


class SingleResponse(APIResponse[T], Generic[T]):
    """Response wrapper for single-item endpoints."""

    pass
