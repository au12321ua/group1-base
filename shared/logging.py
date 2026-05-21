"""AppLogger: structured JSON logging with automatic request_id injection."""

import json
import logging
import logging.handlers
import os
import sys
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# ── ContextVar for X-Request-ID propagation across async tasks ──────────────

_request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def set_request_id(request_id: str) -> None:
    """Set the request_id for the current async context."""
    _request_id_var.set(request_id)


def get_request_id() -> str:
    """Get the request_id for the current async context."""
    return _request_id_var.get()


# ── JSON Formatter ───────────────────────────────────────────────────────────

class JsonFormatter(logging.Formatter):
    """Formats log records as JSON with automatic context injection."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=UTC)
        log_entry: dict[str, Any] = {
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        request_id = get_request_id()
        if request_id:
            log_entry["request_id"] = request_id

        # Merge extra context fields from logging.Logger.log(..., extra={...})
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message",
            }:
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ── AppLogger ────────────────────────────────────────────────────────────────

# Mapping from rotation config value to TimedRotatingFileHandler 'when' parameter
_ROTATION_WHEN: dict[str, str] = {
    "daily": "midnight",
    "hourly": "H",
    "weekly": "W0",
}


# Set of directories already created to avoid redundant mkdir syscalls
_dirs_created: set[str] = set()


class AppLogger:
    """Unified logger with JSON output, request_id injection, and four-level logging.

    Supports console and file output with daily rotation and configurable retention.
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        service_name: str = "",
        output: str = "console",
        log_dir: str = "/var/log/stss/",
        rotation: str = "daily",
        retention: int = 30,
    ) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.handlers.clear()
        self._service_name = service_name

        handler: logging.Handler
        if output == "file":
            if log_dir not in _dirs_created:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
                _dirs_created.add(log_dir)
            log_file = os.path.join(log_dir, f"{service_name or name}.log")
            when = _ROTATION_WHEN.get(rotation, "midnight")
            handler = logging.handlers.TimedRotatingFileHandler(
                log_file,
                when=when,
                interval=1,
                backupCount=retention,
                encoding="utf-8",
            )
        else:
            handler = logging.StreamHandler(sys.stdout)

        handler.setFormatter(JsonFormatter())
        self._logger.addHandler(handler)

    def set_level(self, level: str) -> None:
        """Update the log level at runtime."""
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def _log(self, level: int, message: str, **context: Any) -> None:
        extra: dict[str, Any] = {}
        if self._service_name:
            extra["service"] = self._service_name
        exc_info = context.pop("exc_info", False)
        extra.update(context)
        self._logger.log(level, message, extra=extra or None, exc_info=exc_info)

    def debug(self, message: str, **context: Any) -> None:
        self._log(logging.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> None:
        self._log(logging.INFO, message, **context)

    def warn(self, message: str, **context: Any) -> None:
        self._log(logging.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._log(logging.ERROR, message, **context)


# ── Factory ──────────────────────────────────────────────────────────────────

def get_logger(
    name: str,
    service_name: str = "",
    level: str | None = None,
) -> AppLogger:
    """Factory for creating AppLogger instances.

    Reads LOG_LEVEL, LOG_OUTPUT, LOG_DIR, LOG_ROTATION, LOG_RETENTION
    from environment variables (or .env via python-dotenv).
    """
    resolved_level = level or os.getenv("LOG_LEVEL", "INFO")
    output = os.getenv("LOG_OUTPUT", "console")
    log_dir = os.getenv("LOG_DIR", "/var/log/stss/")
    rotation = os.getenv("LOG_ROTATION", "daily")
    retention = int(os.getenv("LOG_RETENTION", "30"))

    return AppLogger(
        name=name,
        level=resolved_level,
        service_name=service_name,
        output=output,
        log_dir=log_dir,
        rotation=rotation,
        retention=retention,
    )


# ── LoggingService ───────────────────────────────────────────────────────────

class LoggingService:
    """Unified logging entry point.

    Normal logs delegate to AppLogger; high-risk audit operations are written
    via an injected audit_writer callable (wired to AuditService at startup).
    """

    def __init__(
        self,
        name: str,
        service_name: str = "",
        audit_writer: Callable[..., Any] | None = None,
    ) -> None:
        self._logger = get_logger(name, service_name=service_name)
        self._audit_writer = audit_writer

    def set_level(self, level: str) -> None:
        self._logger.set_level(level)

    def debug(self, message: str, **context: Any) -> None:
        self._logger.debug(message, **context)

    def info(self, message: str, **context: Any) -> None:
        self._logger.info(message, **context)

    def warn(self, message: str, **context: Any) -> None:
        self._logger.warn(message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._logger.error(message, **context)

    async def write_audit_log(self, **log_data: Any) -> None:
        """Write an audit log entry for a high-risk operation.

        Requires audit_writer callable to be injected at construction time.
        """
        if self._audit_writer is None:
            raise NotImplementedError(
                "write_audit_log: no audit_writer configured"
            )
        await self._audit_writer(**log_data)


# ── FastAPI Middleware ───────────────────────────────────────────────────────

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Extracts X-Request-ID from the incoming request header or generates one.

    Stores the request_id in ContextVar so AppLogger can inject it automatically.
    Also sets X-Request-ID on the response header for end-to-end tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]
        set_request_id(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs each HTTP request with method, path, status, and duration in ms."""

    def __init__(self, app: Any, logger: AppLogger | None = None) -> None:
        super().__init__(app)
        self._logger = logger or get_logger("request")

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        start = time.perf_counter()
        status_code = 0
        failed = False
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            failed = True
            raise
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            if failed:
                self._logger.error(
                    "Request failed",
                    method=request.method,
                    path=request.url.path,
                    duration_ms=duration_ms,
                    exc_info=True,
                )
            else:
                self._logger.info(
                    "Request completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=status_code,
                    duration_ms=duration_ms,
                )
