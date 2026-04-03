"""Metrics endpoints for triage."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.deps import get_db, get_profissional_atual
from backend.app.models.profissional import Profissional
from backend.app.models.triagem import Triagem
from backend.app.services.classification import RiscoNivel

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/triagem")
async def obter_metricas_triagem(
    db: AsyncSession = Depends(get_db),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> dict[str, object]:
    """Return aggregated triage metrics."""
    if not settings.DEBUG and profissional_atual.email != "admin@triagem.local":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )

    total_triagens = await db.scalar(select(func.count()).select_from(Triagem)) or 0

    linhas_por_nivel = await db.execute(
        select(Triagem.nivel_calculado, func.count()).group_by(Triagem.nivel_calculado)
    )
    triagens_por_nivel = {nivel.value: 0 for nivel in RiscoNivel}
    for nivel, quantidade in linhas_por_nivel.all():
        triagens_por_nivel[nivel.value] = int(quantidade)

    total_confirmadas = await db.scalar(
        select(func.count())
        .select_from(Triagem)
        .where(Triagem.nivel_confirmado.is_not(None))
    ) or 0

    total_corrigidas = await db.scalar(
        select(func.count())
        .select_from(Triagem)
        .where(
            Triagem.nivel_confirmado.is_not(None),
            Triagem.nivel_confirmado != Triagem.nivel_calculado,
        )
    ) or 0

    amostras_disponiveis_ml = await db.scalar(
        select(func.count())
        .select_from(Triagem)
        .where(Triagem.usado_em_treino.is_(False), Triagem.nivel_confirmado.is_not(None))
    ) or 0

    media_confianca = await db.scalar(select(func.avg(Triagem.confianca))) or 0.0
    triagens_ultimas_24h = await db.scalar(
        select(func.count())
        .select_from(Triagem)
        .where(Triagem.criado_em >= datetime.now(UTC) - timedelta(hours=24))
    ) or 0

    taxa_correcao = 0.0
    if total_confirmadas > 0:
        taxa_correcao = round((total_corrigidas / total_confirmadas) * 100, 2)

    return {
        "total_triagens": int(total_triagens),
        "triagens_por_nivel": triagens_por_nivel,
        "taxa_correcao_profissional": taxa_correcao,
        "amostras_disponiveis_ml": int(amostras_disponiveis_ml),
        "media_confianca": round(float(media_confianca), 4),
        "triagens_ultimas_24h": int(triagens_ultimas_24h),
    }
