"""Structured logging configuration."""

from __future__ import annotations

import contextvars
import json
import logging
from datetime import UTC, datetime

from backend.app.core.config import settings

_contexto_logs: contextvars.ContextVar[dict[str, object]] = contextvars.ContextVar(
    "contexto_logs",
    default={},
)


class JsonFormatter(logging.Formatter):
    """Format logs as JSON payloads."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a log record to JSON."""
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(_contexto_logs.get())

        extras = {
            chave: valor
            for chave, valor in record.__dict__.items()
            if chave
            not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }
        }
        payload.update(extras)

        if record.exc_info is not None:
            exc_type = record.exc_info[0]
            exc_value = record.exc_info[1]
            payload["exc_type"] = exc_type.__name__ if exc_type else "Exception"
            payload["exc_message"] = str(exc_value)

        return json.dumps(payload, ensure_ascii=False)


class DevFormatter(logging.Formatter):
    """Format logs for local development."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a log record to a readable line."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        contexto = " ".join(f"{chave}={valor}" for chave, valor in _contexto_logs.get().items())
        base = f"[{timestamp}] {record.levelname:<8} {record.name}: {record.getMessage()}"
        return f"{base} {contexto}".strip()


def bind_log_context(**fields: object) -> None:
    """Bind fields to the request log context."""
    contexto = dict(_contexto_logs.get())
    contexto.update({chave: valor for chave, valor in fields.items() if valor is not None})
    _contexto_logs.set(contexto)


def clear_log_context() -> None:
    """Clear the active log context."""
    _contexto_logs.set({})


def configure_logging() -> None:
    """Configure root logging handlers."""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(DevFormatter() if settings.DEBUG else JsonFormatter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger."""
    return logging.getLogger(name)
