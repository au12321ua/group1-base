"""Auth Service specific exception handlers (re-exports shared exceptions)."""

from shared.exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ResourceNotFoundError,
    ServiceCredentialInvalidError,
    TokenExpiredError,
)

__all__ = [
    "AppError",
    "AuthenticationError",
    "AuthorizationError",
    "ResourceNotFoundError",
    "BusinessRuleError",
    "AccountLockedError",
    "AccountDisabledError",
    "TokenExpiredError",
    "ServiceCredentialInvalidError",
]
