"""Patient CRUD endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.deps import (
    get_db,
    get_paciente_repository,
    get_profissional_atual,
)
from backend.app.models.profissional import Profissional
from backend.app.repositories.paciente_repository import PacienteRepository
from backend.app.schemas.paciente import PacienteCreate, PacienteOut, PacienteUpdate

router = APIRouter(
    prefix="/pacientes",
    tags=["pacientes"],
    dependencies=[Depends(get_profissional_atual)],
)


@router.post("/", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
async def criar_paciente(
    dados: PacienteCreate,
    db: AsyncSession = Depends(get_db),
    repo: PacienteRepository = Depends(get_paciente_repository),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> PacienteOut:
    """Create a patient."""
    del profissional_atual
    paciente = await repo.criar(db, dados)
    return PacienteOut.model_validate(paciente)


@router.get("/{id}", response_model=PacienteOut)
async def buscar_paciente(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    repo: PacienteRepository = Depends(get_paciente_repository),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> PacienteOut:
    """Fetch a patient by id."""
    del profissional_atual
    paciente = await repo.buscar_por_id(db, id)
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente nao encontrado.")
    return PacienteOut.model_validate(paciente)


@router.get("/", response_model=list[PacienteOut])
async def listar_pacientes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    repo: PacienteRepository = Depends(get_paciente_repository),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> list[PacienteOut]:
    """List patients with pagination."""
    del profissional_atual
    pacientes = await repo.listar(db, skip, limit)
    return [PacienteOut.model_validate(paciente) for paciente in pacientes]


@router.patch("/{id}", response_model=PacienteOut)
async def atualizar_paciente(
    id: uuid.UUID,
    dados: PacienteUpdate,
    db: AsyncSession = Depends(get_db),
    repo: PacienteRepository = Depends(get_paciente_repository),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> PacienteOut:
    """Partially update a patient."""
    del profissional_atual
    paciente = await repo.atualizar(db, id, dados)
    if paciente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente nao encontrado.")
    return PacienteOut.model_validate(paciente)
