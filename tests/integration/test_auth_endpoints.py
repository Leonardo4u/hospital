from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from backend.app.core.config import settings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_registro_retorna_201_e_profissional_sem_senha(client) -> None:
    response = await client.post("/api/v1/auth/registro", json={"nome": "Novo", "email": "novo@triagem.com", "senha": "Senha@123", "crm": "123456", "cargo": "MEDICO"})
    body = response.json()
    assert response.status_code == 201 and "senha" not in body and "senha_hash" not in body


@pytest.mark.integration
@pytest.mark.asyncio
async def test_registro_email_duplicado_retorna_409(client) -> None:
    payload = {"nome": "Novo", "email": "duplicado@triagem.com", "senha": "Senha@123", "crm": "123456", "cargo": "MEDICO"}
    await client.post("/api/v1/auth/registro", json=payload)
    response = await client.post("/api/v1/auth/registro", json=payload)
    assert response.status_code == 409


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_valido_retorna_tokens(client) -> None:
    await client.post("/api/v1/auth/registro", json={"nome": "Novo", "email": "login@triagem.com", "senha": "Senha@123", "crm": "123456", "cargo": "MEDICO"})
    response = await client.post("/api/v1/auth/login", json={"email": "login@triagem.com", "senha": "Senha@123"})
    assert set(response.json().keys()) == {"access_token", "refresh_token", "token_type"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_senha_errada_retorna_401(client) -> None:
    await client.post("/api/v1/auth/registro", json={"nome": "Novo", "email": "erro@triagem.com", "senha": "Senha@123", "crm": "123456", "cargo": "MEDICO"})
    response = await client.post("/api/v1/auth/login", json={"email": "erro@triagem.com", "senha": "SenhaErrada"})
    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_valido_retorna_novos_tokens(client) -> None:
    await client.post("/api/v1/auth/registro", json={"nome": "Novo", "email": "refresh@triagem.com", "senha": "Senha@123", "crm": "123456", "cargo": "MEDICO"})
    login = await client.post("/api/v1/auth/login", json={"email": "refresh@triagem.com", "senha": "Senha@123"})
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert set(response.json().keys()) == {"access_token", "refresh_token", "token_type"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_token_expirado_retorna_401(client) -> None:
    token = jwt.encode(
        {"sub": "123", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_endpoint_protegido_sem_token_retorna_401(client) -> None:
    response = await client.get("/api/v1/pacientes/")
    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_endpoint_protegido_com_token_valido_retorna_200(client) -> None:
    await client.post("/api/v1/auth/registro", json={"nome": "Novo", "email": "me@triagem.com", "senha": "Senha@123", "crm": "123456", "cargo": "MEDICO"})
    login = await client.post("/api/v1/auth/login", json={"email": "me@triagem.com", "senha": "Senha@123"})
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert response.status_code == 200
