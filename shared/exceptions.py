"""Unified exception hierarchy for both services."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, code: int, message: str, detail: str = "") -> None:
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


class AuthenticationException(AppException):
    """Authentication failures (invalid credentials, expired tokens)."""

    def __init__(self, message: str = "Authentication failed", code: int = 1001) -> None:
        super().__init__(code=code, message=message)


class AuthorizationException(AppException):
    """Authorization failures (insufficient permissions)."""

    def __init__(self, message: str = "Insufficient permissions", code: int = 4030) -> None:
        super().__init__(code=code, message=message)


class ResourceNotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", identifier: str = "") -> None:
        detail = f"{resource} not found" + (f": {identifier}" if identifier else "")
        super().__init__(code=4040, message=detail)


class BusinessRuleException(AppException):
    """Business rule violations (e.g. duplicate, state conflict)."""

    def __init__(self, message: str, code: int = 4090) -> None:
        super().__init__(code=code, message=message)


class AccountLockedException(AppException):
    """Account locked due to repeated failed login attempts."""

    def __init__(self, message: str = "Account locked, please try again later") -> None:
        super().__init__(code=1003, message=message)


class AccountDisabledException(AppException):
    """Account has been disabled."""

    def __init__(self, message: str = "Account has been disabled") -> None:
        super().__init__(code=1002, message=message)


class TokenExpiredException(AuthenticationException):
    """Token has expired."""

    def __init__(self, message: str = "Token has expired") -> None:
        super().__init__(message=message, code=1004)


class ServiceCredentialInvalidException(AuthenticationException):
    """Service credential (client_id/client_secret) is invalid."""

    def __init__(self, message: str = "Service credential invalid") -> None:
        super().__init__(message=message, code=1007)
