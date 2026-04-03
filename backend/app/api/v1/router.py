"""API v1 router composition."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.health import router as health_router
from backend.app.api.v1.endpoints.metrics import router as metrics_router
from backend.app.api.v1.endpoints.pacientes import router as pacientes_router
from backend.app.api.v1.endpoints.triagens import router as triagens_router

router = APIRouter()
router.include_router(health_router)
router.include_router(metrics_router)
router.include_router(auth_router)
router.include_router(pacientes_router)
router.include_router(triagens_router)
