"""Tests for info-side backward-compatible re-exports."""

from info_service.core import exceptions as info_exceptions
from info_service.crud import audit_log_crud as info_audit_log_crud
from shared.crud.audit_log_crud import AuditLogCRUD, audit_log_crud
from shared.exceptions import (
    AccountDisabledError,
    AccountLockedError,
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ResourceNotFoundError,
)


def test_info_exception_module_reexports_shared_types() -> None:
    assert info_exceptions.AppError is AppError
    assert info_exceptions.AuthenticationError is AuthenticationError
    assert info_exceptions.AuthorizationError is AuthorizationError
    assert info_exceptions.ResourceNotFoundError is ResourceNotFoundError
    assert info_exceptions.BusinessRuleError is BusinessRuleError
    assert info_exceptions.AccountLockedError is AccountLockedError
    assert info_exceptions.AccountDisabledError is AccountDisabledError
    assert set(info_exceptions.__all__) == {
        "AppError",
        "AuthenticationError",
        "AuthorizationError",
        "ResourceNotFoundError",
        "BusinessRuleError",
        "AccountLockedError",
        "AccountDisabledError",
    }


def test_audit_log_crud_module_reexports_shared_symbols() -> None:
    assert info_audit_log_crud.AuditLogCRUD is AuditLogCRUD
    assert info_audit_log_crud.audit_log_crud is audit_log_crud
    assert info_audit_log_crud.__all__ == ["AuditLogCRUD", "audit_log_crud"]
