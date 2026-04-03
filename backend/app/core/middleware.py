"""Middleware for request ids and structured HTTP logging."""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.app.core.logging_config import bind_log_context, clear_log_context, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a request id to each response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Generate and propagate request ids."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        bind_log_context(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request lifecycle with structured fields."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Emit structured logs for request start and end."""
        inicio = time.perf_counter()
        bind_log_context(method=request.method, path=request.url.path)
        logger.info("request_started")

        try:
            response = await call_next(request)
        except Exception:
            bind_log_context(status_code=500, duration_ms=round((time.perf_counter() - inicio) * 1000, 2))
            logger.exception("request_failed")
            clear_log_context()
            raise

        bind_log_context(
            status_code=response.status_code,
            duration_ms=round((time.perf_counter() - inicio) * 1000, 2),
        )
        logger.info("request_finished")
        clear_log_context()
        return response
