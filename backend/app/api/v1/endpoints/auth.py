"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from backend.app.core.deps import get_auth_service, get_profissional_atual
from backend.app.models.profissional import Profissional
from backend.app.schemas.profissional import LoginIn, ProfissionalCreate, ProfissionalOut, TokenOut
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenIn(BaseModel):
    """Input schema for token refresh."""

    refresh_token: str


@router.post("/registro", response_model=ProfissionalOut, status_code=status.HTTP_201_CREATED)
async def registrar_profissional(
    dados: ProfissionalCreate,
    service: AuthService = Depends(get_auth_service),
) -> ProfissionalOut:
    """Register a new professional."""
    return await service.registrar(dados)


@router.post("/login", response_model=TokenOut)
async def login(
    dados: LoginIn,
    service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    """Authenticate and return JWT tokens."""
    return await service.login(dados)


@router.post("/refresh", response_model=TokenOut)
def refresh(
    dados: RefreshTokenIn,
    service: AuthService = Depends(get_auth_service),
) -> TokenOut:
    """Refresh an authentication token pair."""
    return service.renovar_token(dados.refresh_token)


@router.get("/me", response_model=ProfissionalOut)
def me(
    profissional_atual: Profissional = Depends(get_profissional_atual),
    service: AuthService = Depends(get_auth_service),
) -> ProfissionalOut:
    """Return the current authenticated professional."""
    return service.obter_me(profissional_atual)
