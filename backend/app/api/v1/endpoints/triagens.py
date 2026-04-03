"""Triage endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, status

from backend.app.core.deps import get_profissional_atual, get_triagem_service
from backend.app.models.profissional import Profissional
from backend.app.schemas.triagem import ConfirmacaoIn, TriagemCreate, TriagemCreatedOut, TriagemOut
from backend.app.services.triagem_service import TriagemService

router = APIRouter(
    prefix="/triagens",
    tags=["triagens"],
    dependencies=[Depends(get_profissional_atual)],
)


@router.post("/", response_model=TriagemCreatedOut, status_code=status.HTTP_201_CREATED)
async def classificar_triagem(
    dados: TriagemCreate,
    request: Request,
    service: TriagemService = Depends(get_triagem_service),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> TriagemCreatedOut:
    """Create a triage classification."""
    ip = request.client.host if request.client is not None else ""
    return await service.classificar(dados, profissional_atual.id, ip)


@router.get("/{id}", response_model=TriagemOut)
async def buscar_triagem(
    id: uuid.UUID,
    service: TriagemService = Depends(get_triagem_service),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> TriagemOut:
    """Fetch a triage by id."""
    return await service.buscar(id, profissional_atual.id)


@router.post("/{id}/confirmar", response_model=TriagemOut)
async def confirmar_triagem(
    id: uuid.UUID,
    dados: ConfirmacaoIn,
    request: Request,
    service: TriagemService = Depends(get_triagem_service),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> TriagemOut:
    """Confirm a triage result."""
    ip = request.client.host if request.client is not None else ""
    return await service.confirmar(id, dados, profissional_atual.id, profissional_atual.cargo, ip)


@router.get("/paciente/{paciente_id}", response_model=list[TriagemOut])
async def listar_triagens_por_paciente(
    paciente_id: uuid.UUID,
    service: TriagemService = Depends(get_triagem_service),
    profissional_atual: Profissional = Depends(get_profissional_atual),
) -> list[TriagemOut]:
    """List triages for a given patient."""
    del profissional_atual
    return await service.listar_por_paciente(paciente_id)
