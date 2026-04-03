from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_retorna_200_com_banco_ativo(client) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_contem_status_banco_e_classificador(client) -> None:
    body = (await client.get("/api/v1/health")).json()
    assert {"banco", "classificador"}.issubset(body["componentes"].keys())


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_contem_info_ml_com_amostras_zero(client) -> None:
    body = (await client.get("/api/v1/health")).json()
    assert body["componentes"]["ml"]["amostras_confirmadas"] == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_sem_autenticacao(client) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
