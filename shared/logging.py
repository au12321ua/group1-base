"""AppLogger: structured JSON logging with automatic request_id injection."""

import json
import logging
import sys
import time
import warnings
from contextvars import ContextVar
from typing import Any, Optional

# ContextVar for X-Request-ID propagation across async tasks
_request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def set_request_id(request_id: str) -> None:
    """Set the request_id for the current async context."""
    _request_id_var.set(request_id)


def get_request_id() -> str:
    """Get the request_id for the current async context."""
    return _request_id_var.get()


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON with automatic context injection."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(record.created)
            ),
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

        # Merge extra context fields
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


class AppLogger:
    """Unified logger with JSON output, request_id injection, and four-level logging."""

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        service_name: str = "",
        output: str = "console",
    ) -> None:
        warnings.warn("TODO: implement AppLogger fully - file output, rotation")
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.handlers.clear()
        self._service_name = service_name

        handler: logging.Handler
        if output == "console":
            handler = logging.StreamHandler(sys.stdout)
        else:
            handler = logging.StreamHandler(sys.stdout)  # placeholder for file handler

        handler.setFormatter(JsonFormatter())
        self._logger.addHandler(handler)

    def _log(self, level: int, message: str, **context: Any) -> None:
        extra: dict[str, Any] = {}
        if self._service_name:
            extra["service"] = self._service_name
        extra.update(context)
        self._logger.log(level, message, extra=extra)

    def debug(self, message: str, **context: Any) -> None:
        self._log(logging.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> None:
        self._log(logging.INFO, message, **context)

    def warn(self, message: str, **context: Any) -> None:
        self._log(logging.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._log(logging.ERROR, message, **context)


def get_logger(
    name: str,
    service_name: str = "",
    level: Optional[str] = None,
) -> AppLogger:
    """Factory for creating AppLogger instances."""
    warnings.warn("TODO: implement get_logger - read LOG_LEVEL from config")
    return AppLogger(name=name, level=level or "INFO", service_name=service_name)
