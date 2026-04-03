"""Health check endpoints."""

from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.deps import get_classifier, get_db
from backend.app.services.classification import Classifier, EntradaClassificacao, SinaisVitais

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck(
    db: AsyncSession = Depends(get_db),
    classifier: Classifier = Depends(get_classifier),
) -> JSONResponse:
    """Return health information for core services."""
    banco_status = {"status": "falha", "latencia_ms": 0.0}
    classificador_status = {"status": "falha", "motor": "regras"}
    ml_status = {
        "status": "inativo",
        "amostras_confirmadas": 0,
        "minimo_necessario": settings.MIN_AMOSTRAS_ML,
    }

    try:
        inicio = perf_counter()
        await db.execute(text("SELECT 1"))
        banco_status = {
            "status": "ok",
            "latencia_ms": round((perf_counter() - inicio) * 1000, 2),
        }
    except Exception:
        banco_status = {"status": "falha", "latencia_ms": 0.0}

    try:
        classifier.classificar(
            EntradaClassificacao(
                sinais_vitais=SinaisVitais(
                    frequencia_cardiaca=80,
                    pressao_sistolica=120,
                    pressao_diastolica=80,
                    saturacao_o2=98.0,
                    temperatura=36.8,
                    frequencia_respiratoria=16,
                    glasgow=15,
                ),
                sintomas=[],
                idade_anos=35,
                queixa_principal="teste de saude do classificador",
            )
        )
        classificador_status = {"status": "ok", "motor": "regras"}
    except Exception:
        classificador_status = {"status": "falha", "motor": "regras"}

    http_status = status.HTTP_200_OK
    status_geral = "ok"
    if banco_status["status"] == "falha" or classificador_status["status"] == "falha":
        status_geral = "falha"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    elif banco_status["latencia_ms"] > 500:
        status_geral = "degradado"

    return JSONResponse(
        status_code=http_status,
        content={
            "status": status_geral,
            "versao": "1.0.0",
            "componentes": {
                "banco": banco_status,
                "classificador": classificador_status,
                "ml": ml_status,
            },
        },
    )
