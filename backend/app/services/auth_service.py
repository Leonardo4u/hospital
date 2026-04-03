"""Authentication orchestration service."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import (
    criar_access_token,
    criar_refresh_token,
    decodificar_token,
    hash_senha,
    verificar_senha,
)
from backend.app.models.profissional import Profissional
from backend.app.repositories.profissional_repository import ProfissionalRepository
from backend.app.schemas.profissional import LoginIn, ProfissionalCreate, ProfissionalOut, TokenOut


class AuthService:
    """Service responsible for authentication workflows."""

    def __init__(self, repo: ProfissionalRepository, db: AsyncSession) -> None:
        """Store injected dependencies for auth workflows."""
        self._repo = repo
        self._db = db

    async def registrar(self, dados: ProfissionalCreate) -> ProfissionalOut:
        """Register a new professional account."""
        existente = await self._repo.buscar_por_email(self._db, str(dados.email))
        if existente is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email ja cadastrado.",
            )

        profissional = await self._repo.criar(
            self._db,
            dados.model_copy(update={"senha": hash_senha(dados.senha)}),
        )
        return ProfissionalOut.model_validate(profissional)

    async def login(self, dados: LoginIn) -> TokenOut:
        """Authenticate a professional and issue tokens."""
        profissional = await self._repo.buscar_por_email(self._db, str(dados.email))
        if (
            profissional is None
            or not profissional.ativo
            or not verificar_senha(dados.senha, profissional.senha_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais invalidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        subject = {"sub": str(profissional.id)}
        return TokenOut(
            access_token=criar_access_token(subject),
            refresh_token=criar_refresh_token(subject),
        )

    def renovar_token(self, refresh_token: str) -> TokenOut:
        """Issue a fresh token pair from a refresh token."""
        payload = decodificar_token(refresh_token)
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        dados = {"sub": str(subject)}
        return TokenOut(
            access_token=criar_access_token(dados),
            refresh_token=criar_refresh_token(dados),
        )

    def obter_me(self, profissional: Profissional) -> ProfissionalOut:
        """Return the authenticated professional profile."""
        return ProfissionalOut.model_validate(profissional)
