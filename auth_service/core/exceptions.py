"""Auth Service specific exception handlers (re-exports shared exceptions)."""

from shared.exceptions import (
    AccountDisabledException,
    AccountLockedException,
    AppException,
    AuthenticationException,
    AuthorizationException,
    BusinessRuleException,
    ResourceNotFoundException,
    ServiceCredentialInvalidException,
    TokenExpiredException,
)

__all__ = [
    "AppException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "BusinessRuleException",
    "AccountLockedException",
    "AccountDisabledException",
    "TokenExpiredException",
    "ServiceCredentialInvalidException",
]
