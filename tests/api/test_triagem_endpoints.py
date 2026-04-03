"""API tests for triage endpoints."""

from __future__ import annotations

import os
import uuid
from datetime import date

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DEBUG", "false")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.core.deps import get_db
from backend.app.core.security import criar_access_token, hash_senha
from backend.app.main import app
from backend.app.models.audit_log import AuditLog
from backend.app.models.base import Base
from backend.app.models.paciente import Paciente, SexoPaciente
from backend.app.models.profissional import CargoProfissional, Profissional


@pytest_asyncio.fixture
async def db_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    yield session_factory
    await engine.dispose()


@pytest_asyncio.fixture
async def app_fixture(db_session_factory: async_sessionmaker[AsyncSession]):
    async def override_get_db():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_fixture) -> AsyncClient:
    transport = ASGITransport(app=app_fixture)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest_asyncio.fixture
async def profissional_token(
    db_session_factory: async_sessionmaker[AsyncSession],
) -> str:
    async with db_session_factory() as session:
        profissional = Profissional(
            nome="Dra. Ana",
            email="ana@example.com",
            senha_hash=hash_senha("segredo123"),
            crm="12345",
            cargo=CargoProfissional.MEDICO,
            ativo=True,
        )
        session.add(profissional)
        await session.commit()
        await session.refresh(profissional)
        return criar_access_token({"sub": str(profissional.id)})


@pytest_asyncio.fixture
async def paciente_id(db_session_factory: async_sessionmaker[AsyncSession]) -> uuid.UUID:
    async with db_session_factory() as session:
        paciente = Paciente(
            nome_completo="Paciente API",
            data_nascimento=date(1992, 5, 20),
            cpf="98765432100",
            sexo=SexoPaciente.M,
            contato_emergencia="Pai",
        )
        session.add(paciente)
        await session.commit()
        await session.refresh(paciente)
        return paciente.id


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _payload(paciente_id_value: uuid.UUID) -> dict[str, object]:
    return {
        "paciente_id": str(paciente_id_value),
        "sinais_vitais": {
            "frequencia_cardiaca": 110,
            "pressao_sistolica": 120,
            "pressao_diastolica": 80,
            "saturacao_o2": 96.0,
            "temperatura": 38.0,
            "frequencia_respiratoria": 18,
            "glasgow": 15,
        },
        "sintomas": [
            {"codigo": "dor_toracica", "descricao": "Dor toracica", "peso": 0.8},
        ],
        "queixa_principal": "Dor toracica intensa",
    }


@pytest.mark.asyncio
async def test_classificar_retorna_apenas_id_e_criado_em(
    client: AsyncClient,
    profissional_token: str,
    paciente_id: uuid.UUID,
) -> None:
    response = await client.post(
        "/api/v1/triagens/",
        json=_payload(paciente_id),
        headers=_headers(profissional_token),
    )

    body = response.json()
    assert response.status_code == 201
    assert set(body.keys()) == {"id", "criado_em"}


@pytest.mark.asyncio
async def test_buscar_triagem_retorna_resultado_completo(
    client: AsyncClient,
    profissional_token: str,
    paciente_id: uuid.UUID,
) -> None:
    criar = await client.post(
        "/api/v1/triagens/",
        json=_payload(paciente_id),
        headers=_headers(profissional_token),
    )
    triagem_id = criar.json()["id"]

    response = await client.get(
        f"/api/v1/triagens/{triagem_id}",
        headers=_headers(profissional_token),
    )

    body = response.json()
    assert response.status_code == 200
    assert "nivel_calculado" in body
    assert "justificativa" in body
    assert "discriminadores_ativados" in body


@pytest.mark.asyncio
async def test_classificar_sem_auth_retorna_401(
    client: AsyncClient,
    paciente_id: uuid.UUID,
) -> None:
    response = await client.post("/api/v1/triagens/", json=_payload(paciente_id))

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sinais_vitais_invalidos_retornam_422(
    client: AsyncClient,
    profissional_token: str,
    paciente_id: uuid.UUID,
) -> None:
    payload = _payload(paciente_id)
    payload["sinais_vitais"]["glasgow"] = 20

    response = await client.post(
        "/api/v1/triagens/",
        json=payload,
        headers=_headers(profissional_token),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_confirmar_triagem_duas_vezes_retorna_409(
    client: AsyncClient,
    profissional_token: str,
    paciente_id: uuid.UUID,
) -> None:
    criar = await client.post(
        "/api/v1/triagens/",
        json=_payload(paciente_id),
        headers=_headers(profissional_token),
    )
    triagem_id = criar.json()["id"]

    primeira = await client.post(
        f"/api/v1/triagens/{triagem_id}/confirmar",
        json={"nivel_confirmado": "laranja"},
        headers=_headers(profissional_token),
    )
    segunda = await client.post(
        f"/api/v1/triagens/{triagem_id}/confirmar",
        json={"nivel_confirmado": "laranja"},
        headers=_headers(profissional_token),
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 409


@pytest.mark.asyncio
async def test_audit_log_criado_apos_classificacao(
    client: AsyncClient,
    db_session_factory: async_sessionmaker[AsyncSession],
    profissional_token: str,
    paciente_id: uuid.UUID,
) -> None:
    response = await client.post(
        "/api/v1/triagens/",
        json=_payload(paciente_id),
        headers=_headers(profissional_token),
    )

    assert response.status_code == 201

    async with db_session_factory() as session:
        resultado = await session.execute(select(AuditLog))
        logs = list(resultado.scalars().all())

    assert len(logs) == 1
    assert logs[0].acao == "classificar"
