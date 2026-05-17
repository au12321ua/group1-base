"""Info Service exception handlers (re-exports shared exceptions)."""

from shared.exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ResourceNotFoundError,
)

__all__ = [
    "AppError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "BusinessRuleError",
    "AccountLockedError",
    "AccountDisabledError",
]
