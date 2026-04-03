"""Repository for professional persistence operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.profissional import Profissional
from backend.app.schemas.profissional import ProfissionalCreate


class ProfissionalRepository:
    """Data access for professionals."""

    async def criar(self, db: AsyncSession, dados: ProfissionalCreate) -> Profissional:
        """Persist a new professional."""
        profissional = Profissional(
            nome=dados.nome,
            email=str(dados.email),
            senha_hash=dados.senha,
            crm=dados.crm,
            cargo=dados.cargo,
        )
        db.add(profissional)
        await db.commit()
        await db.refresh(profissional)
        return profissional

    async def buscar_por_email(self, db: AsyncSession, email: str) -> Profissional | None:
        """Fetch a professional by email."""
        resultado = await db.execute(select(Profissional).where(Profissional.email == email))
        return resultado.scalar_one_or_none()

    async def buscar_por_id(self, db: AsyncSession, id: uuid.UUID) -> Profissional | None:
        """Fetch a professional by id."""
        resultado = await db.execute(select(Profissional).where(Profissional.id == id))
        return resultado.scalar_one_or_none()

    async def listar(self, db: AsyncSession, skip: int, limit: int) -> list[Profissional]:
        """List professionals with pagination."""
        resultado = await db.execute(select(Profissional).offset(skip).limit(limit))
        return list(resultado.scalars().all())
