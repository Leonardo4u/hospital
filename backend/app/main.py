"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.app.api.v1.router import router as api_v1_router
from backend.app.core.config import settings
from backend.app.core.logging_config import configure_logging, get_logger
from backend.app.core.middleware import LoggingMiddleware, RequestIDMiddleware
from backend.app.db.session import engine, init_db

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Run startup and shutdown checks."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    if settings.DEBUG:
        await init_db()
    yield

app = FastAPI(
    title="Triagem Inteligente",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(api_v1_router, prefix="/api/v1")


@app.exception_handler(ValueError)
async def handle_value_error(_: Request, exc: ValueError) -> JSONResponse:
    """Translate domain validation errors to HTTP 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc), "error": "validation_error"},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    """Translate unexpected exceptions to HTTP 500."""
    if isinstance(exc, HTTPException):
        raise exc

    logger.exception("Erro nao tratado na aplicacao.", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor.", "error": "internal_server_error"},
    )
