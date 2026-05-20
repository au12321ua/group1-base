"""Exception-to-APIResponse handlers for FastAPI.

Registers handlers so every AppError (and subclass) is rendered as a
standard APIResponse JSON body with the correct HTTP status code.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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
from shared.response import APIResponse

# ---------------------------------------------------------------------------
# Exception → HTTP status code mapping (most-specific classes first)
# ---------------------------------------------------------------------------
_EXCEPTION_STATUS: dict[type[AppError], int] = {
    TokenExpiredError: 401,
    ServiceCredentialInvalidError: 401,
    AuthenticationError: 401,
    AccountDisabledError: 401,
    AuthorizationError: 403,
    ResourceNotFoundError: 404,
    BusinessRuleError: 409,
    AccountLockedError: 423,
}


def _get_status_code(exc: AppError) -> int:
    """Map an AppError instance to an HTTP status code (500 if unmapped)."""
    return _EXCEPTION_STATUS.get(type(exc), 500)


def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert an AppError into an APIResponse JSON body."""
    if not isinstance(exc, AppError):
        body = APIResponse(
            code=4444,
            message="Unknown error",
        )
        return JSONResponse(
            status_code=500,
            content=body.model_dump(exclude_none=True),
        )

    status_code = _get_status_code(exc)
    body = APIResponse(
        code=exc.code,
        message=exc.message,
        errors=[{"detail": exc.detail}] if exc.detail else None,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(exclude_none=True),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register app_exception_handler for every known AppError subclass.

    The base AppError is registered last as a catch-all for any
    user-defined AppError subclass that isn't explicitly mapped above.
    """
    for exc_class in _EXCEPTION_STATUS:
        app.add_exception_handler(exc_class, app_exception_handler)
    app.add_exception_handler(AppError, app_exception_handler)
