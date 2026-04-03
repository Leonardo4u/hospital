"""Repository for triage persistence operations."""

from __future__ import annotations

from datetime import UTC, datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.triagem import Triagem
from backend.app.services.classification.types import RiscoNivel


class TriagemRepository:
    """Data access for triage records."""

    async def criar(self, db: AsyncSession, modelo: Triagem) -> Triagem:
        """Persist a pre-built triage model."""
        db.add(modelo)
        await db.commit()
        await db.refresh(modelo)
        return modelo

    async def buscar_por_id(self, db: AsyncSession, id: uuid.UUID) -> Triagem | None:
        """Fetch a triage by id."""
        resultado = await db.execute(select(Triagem).where(Triagem.id == id))
        return resultado.scalar_one_or_none()

    async def listar_por_paciente(self, db: AsyncSession, paciente_id: uuid.UUID) -> list[Triagem]:
        """List triages for a given patient."""
        resultado = await db.execute(
            select(Triagem).where(Triagem.paciente_id == paciente_id).order_by(Triagem.criado_em.desc())
        )
        return list(resultado.scalars().all())

    async def confirmar(self, db: AsyncSession, id: uuid.UUID, nivel: RiscoNivel) -> Triagem | None:
        """Confirm a triage level and return the updated record."""
        triagem = await self.buscar_por_id(db, id)
        if triagem is None:
            return None

        triagem.nivel_confirmado = nivel
        triagem.confirmado_em = datetime.now(UTC)
        await db.commit()
        await db.refresh(triagem)
        return triagem

    async def marcar_usado_em_treino(self, db: AsyncSession, id: uuid.UUID) -> None:
        """Mark a triage as used in training."""
        triagem = await self.buscar_por_id(db, id)
        if triagem is None:
            return

        triagem.usado_em_treino = True
        await db.commit()
