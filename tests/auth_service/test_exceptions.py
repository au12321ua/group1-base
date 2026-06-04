"""Tests for auth-side exception re-exports."""

from auth_service.core import exceptions as auth_exceptions
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


def test_auth_exception_module_reexports_shared_types() -> None:
    assert auth_exceptions.AppError is AppError
    assert auth_exceptions.AuthenticationError is AuthenticationError
    assert auth_exceptions.AuthorizationError is AuthorizationError
    assert auth_exceptions.ResourceNotFoundError is ResourceNotFoundError
    assert auth_exceptions.BusinessRuleError is BusinessRuleError
    assert auth_exceptions.AccountLockedError is AccountLockedError
    assert auth_exceptions.AccountDisabledError is AccountDisabledError
    assert auth_exceptions.TokenExpiredError is TokenExpiredError
    assert auth_exceptions.ServiceCredentialInvalidError is ServiceCredentialInvalidError
    assert set(auth_exceptions.__all__) == {
        "AppError",
        "AuthenticationError",
        "AuthorizationError",
        "ResourceNotFoundError",
        "BusinessRuleError",
        "AccountLockedError",
        "AccountDisabledError",
        "TokenExpiredError",
        "ServiceCredentialInvalidError",
    }
