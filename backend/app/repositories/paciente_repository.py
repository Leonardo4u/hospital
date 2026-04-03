"""Repository for patient persistence operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.paciente import Paciente
from backend.app.schemas.paciente import PacienteCreate, PacienteUpdate


class PacienteRepository:
    """Data access for patients."""

    async def criar(self, db: AsyncSession, dados: PacienteCreate) -> Paciente:
        """Persist a new patient."""
        paciente = Paciente(**dados.model_dump())
        db.add(paciente)
        await db.commit()
        await db.refresh(paciente)
        return paciente

    async def buscar_por_id(self, db: AsyncSession, id: uuid.UUID) -> Paciente | None:
        """Fetch a patient by id."""
        resultado = await db.execute(select(Paciente).where(Paciente.id == id))
        return resultado.scalar_one_or_none()

    async def buscar_por_cpf(self, db: AsyncSession, cpf: str) -> Paciente | None:
        """Fetch a patient by CPF."""
        resultado = await db.execute(select(Paciente).where(Paciente.cpf == cpf))
        return resultado.scalar_one_or_none()

    async def listar(self, db: AsyncSession, skip: int, limit: int) -> list[Paciente]:
        """List patients with pagination."""
        resultado = await db.execute(select(Paciente).offset(skip).limit(limit))
        return list(resultado.scalars().all())

    async def atualizar(
        self,
        db: AsyncSession,
        id: uuid.UUID,
        dados: PacienteUpdate,
    ) -> Paciente | None:
        """Update a patient and return the fresh row."""
        paciente = await self.buscar_por_id(db, id)
        if paciente is None:
            return None

        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(paciente, campo, valor)

        await db.commit()
        await db.refresh(paciente)
        return paciente
