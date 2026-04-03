from __future__ import annotations

import os
import sys
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import date
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-suite")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ALLOWED_ORIGINS", "[\"http://localhost\"]")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.deps import get_db
from backend.app.core.security import criar_access_token, hash_senha
from backend.app.main import app
from backend.app.models.audit_log import AuditLog
from backend.app.models.base import Base
from backend.app.models.paciente import Paciente, SexoPaciente
from backend.app.models.profissional import CargoProfissional, Profissional
from backend.app.models.triagem import OrigemClassificacao, Triagem
from backend.app.services.classification import RiscoNivel


@pytest_asyncio.fixture(scope="session")
async def engine():
    motor = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield motor
    await motor.dispose()


@pytest_asyncio.fixture(scope="session")
async def init_tables(engine) -> None:
    import backend.app.models.audit_log  # noqa: F401
    import backend.app.models.paciente  # noqa: F401
    import backend.app.models.profissional  # noqa: F401
    import backend.app.models.triagem  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def db(engine, init_tables) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(delete(table))
        await session.commit()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
    app.dependency_overrides.clear()


@pytest.fixture
def profissional_factory(db: AsyncSession) -> Callable[..., Awaitable[Profissional]]:
    async def _factory(
        *,
        email: str | None = None,
        senha: str = "Senha@123",
        ativo: bool = True,
        cargo: CargoProfissional = CargoProfissional.MEDICO,
    ) -> Profissional:
        profissional = Profissional(
            nome="Profissional Teste",
            email=email or f"{uuid.uuid4()}@triagem.local",
            senha_hash=hash_senha(senha),
            crm=str(uuid.uuid4().int)[:6],
            cargo=cargo,
            ativo=ativo,
        )
        db.add(profissional)
        await db.commit()
        await db.refresh(profissional)
        return profissional

    return _factory


@pytest.fixture
def token_factory() -> Callable[[Profissional], str]:
    def _factory(profissional: Profissional) -> str:
        return criar_access_token({"sub": str(profissional.id)})

    return _factory


@pytest.fixture
def paciente_factory(db: AsyncSession) -> Callable[..., Awaitable[Paciente]]:
    async def _factory(
        *,
        nome: str = "Paciente Teste",
        cpf: str | None = None,
        sexo: SexoPaciente = SexoPaciente.F,
    ) -> Paciente:
        paciente = Paciente(
            nome_completo=nome,
            data_nascimento=date(1990, 1, 1),
            cpf=cpf or str(uuid.uuid4().int)[:11],
            sexo=sexo,
            contato_emergencia="Mae - 11999999999",
        )
        db.add(paciente)
        await db.commit()
        await db.refresh(paciente)
        return paciente

    return _factory


@pytest.fixture
def sinais_vitais_normais() -> dict[str, int | float]:
    return {
        "frequencia_cardiaca": 75,
        "pressao_sistolica": 120,
        "pressao_diastolica": 80,
        "saturacao_o2": 98.0,
        "temperatura": 36.5,
        "frequencia_respiratoria": 16,
        "glasgow": 15,
    }


@pytest.fixture
def sinais_vitais_criticos() -> dict[str, int | float]:
    return {
        "frequencia_cardiaca": 160,
        "pressao_sistolica": 75,
        "pressao_diastolica": 50,
        "saturacao_o2": 84.0,
        "temperatura": 36.5,
        "frequencia_respiratoria": 28,
        "glasgow": 6,
    }


@pytest.fixture
def sinais_vitais_febre() -> dict[str, int | float]:
    return {
        "frequencia_cardiaca": 95,
        "pressao_sistolica": 125,
        "pressao_diastolica": 82,
        "saturacao_o2": 96.0,
        "temperatura": 40.0,
        "frequencia_respiratoria": 20,
        "glasgow": 15,
    }


@pytest.fixture
def sinais_vitais_azul() -> dict[str, int | float]:
    return {
        "frequencia_cardiaca": 68,
        "pressao_sistolica": 118,
        "pressao_diastolica": 76,
        "saturacao_o2": 99.0,
        "temperatura": 36.2,
        "frequencia_respiratoria": 14,
        "glasgow": 15,
    }


@pytest.fixture
def triagem_factory(db: AsyncSession) -> Callable[..., Awaitable[Triagem]]:
    async def _factory(
        *,
        paciente_id: uuid.UUID,
        profissional_id: uuid.UUID,
        nivel_calculado: RiscoNivel = RiscoNivel.AMARELO,
        nivel_confirmado: RiscoNivel | None = None,
    ) -> Triagem:
        triagem = Triagem(
            paciente_id=paciente_id,
            profissional_id=profissional_id,
            sinais_vitais={
                "frequencia_cardiaca": 80,
                "pressao_sistolica": 120,
                "pressao_diastolica": 80,
                "saturacao_o2": 98.0,
                "temperatura": 36.5,
                "frequencia_respiratoria": 16,
                "glasgow": 15,
            },
            sintomas=[{"codigo": "dor_garganta", "descricao": "Dor de garganta", "peso": 0.2}],
            queixa_principal="Queixa de teste",
            nivel_calculado=nivel_calculado,
            nivel_confirmado=nivel_confirmado,
            justificativa="Justificativa de teste",
            discriminadores_ativados=["avaliar_sintomas_leves"],
            confianca=1.0,
            origem=OrigemClassificacao.REGRAS,
            confirmado_em=None,
            usado_em_treino=False,
        )
        db.add(triagem)
        await db.commit()
        await db.refresh(triagem)
        return triagem

    return _factory
