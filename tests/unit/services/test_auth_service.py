from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from jose import jwt

from backend.app.core.config import settings
from backend.app.models.profissional import CargoProfissional, Profissional
from backend.app.schemas.profissional import LoginIn, ProfissionalCreate
from backend.app.services.auth_service import AuthService


def _dados_profissional(email: str = "novo@triagem.com") -> ProfissionalCreate:
    return ProfissionalCreate(
        nome="Profissional Teste",
        email=email,
        senha="Senha@123",
        crm="123456",
        cargo=CargoProfissional.MEDICO,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_registrar_cria_profissional_com_senha_hasheada() -> None:
    repo = AsyncMock()
    repo.buscar_por_email.return_value = None
    repo.criar.return_value = Profissional(
        id=uuid.uuid4(),
        nome="Profissional Teste",
        email="novo@triagem.com",
        senha_hash="$2b$hash",
        crm="123456",
        cargo=CargoProfissional.MEDICO,
        ativo=True,
    )
    service = AuthService(repo, AsyncMock())
    resultado = await service.registrar(_dados_profissional())
    assert resultado.email == "novo@triagem.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_registrar_email_duplicado_retorna_409() -> None:
    repo = AsyncMock()
    repo.buscar_por_email.return_value = object()
    with pytest.raises(HTTPException) as exc:
        await AuthService(repo, AsyncMock()).registrar(_dados_profissional())
    assert exc.value.status_code == 409


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_credenciais_invalidas_retorna_401() -> None:
    repo = AsyncMock()
    repo.buscar_por_email.return_value = None
    with pytest.raises(HTTPException) as exc:
        await AuthService(repo, AsyncMock()).login(LoginIn(email="x@x.com", senha="errada"))
    assert exc.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_profissional_inativo_retorna_401(profissional_factory) -> None:
    profissional = await profissional_factory(ativo=False, email="inativo@triagem.com")
    repo = AsyncMock()
    repo.buscar_por_email.return_value = profissional
    with pytest.raises(HTTPException) as exc:
        await AuthService(repo, AsyncMock()).login(LoginIn(email=profissional.email, senha="Senha@123"))
    assert exc.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_retorna_access_e_refresh_token(profissional_factory) -> None:
    profissional = await profissional_factory(email="ativo@triagem.com")
    repo = AsyncMock()
    repo.buscar_por_email.return_value = profissional
    resultado = await AuthService(repo, AsyncMock()).login(LoginIn(email=profissional.email, senha="Senha@123"))
    assert {"access_token", "refresh_token", "token_type"} == set(resultado.model_dump().keys())


@pytest.mark.unit
@pytest.mark.asyncio
async def test_tokens_decodificaveis_com_secret_key_correta(profissional_factory) -> None:
    profissional = await profissional_factory(email="decodificar@triagem.com")
    repo = AsyncMock()
    repo.buscar_por_email.return_value = profissional
    tokens = await AuthService(repo, AsyncMock()).login(LoginIn(email=profissional.email, senha="Senha@123"))
    payload = jwt.decode(tokens.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == str(profissional.id)


@pytest.mark.unit
def test_refresh_token_invalido_retorna_401() -> None:
    with pytest.raises(HTTPException) as exc:
        AuthService(AsyncMock(), AsyncMock()).renovar_token("token-invalido")
    assert exc.value.status_code == 401
