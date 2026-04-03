"""Async unit tests for the triage repository."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.models.base import Base
from backend.app.models.paciente import Paciente, SexoPaciente
from backend.app.models.profissional import CargoProfissional, Profissional
from backend.app.models.triagem import OrigemClassificacao, Triagem
from backend.app.repositories.triagem_repository import TriagemRepository
from backend.app.services.classification.types import RiscoNivel


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        yield session

    await engine.dispose()


async def _criar_profissional_e_paciente(session: AsyncSession) -> tuple[Profissional, Paciente]:
    profissional = Profissional(
        nome="Dra. Joana",
        email="joana@example.com",
        senha_hash="hash",
        crm="123456",
        cargo=CargoProfissional.MEDICO,
    )
    paciente = Paciente(
        nome_completo="Paciente Teste",
        data_nascimento=date(1990, 1, 1),
        cpf="12345678901",
        sexo=SexoPaciente.F,
        contato_emergencia="Mae",
    )
    session.add_all([profissional, paciente])
    await session.commit()
    await session.refresh(profissional)
    await session.refresh(paciente)
    return profissional, paciente


def _nova_triagem(paciente: Paciente, profissional: Profissional) -> Triagem:
    return Triagem(
        paciente_id=paciente.id,
        profissional_id=profissional.id,
        sinais_vitais={
            "frequencia_cardiaca": 90,
            "pressao_sistolica": 120,
            "pressao_diastolica": 80,
            "saturacao_o2": 98.0,
            "temperatura": 37.0,
            "frequencia_respiratoria": 16,
            "glasgow": 15,
        },
        sintomas=[{"codigo": "dor_toracica", "descricao": "Dor toracica", "peso": 0.9}],
        queixa_principal="Dor toracica",
        nivel_calculado=RiscoNivel.LARANJA,
        nivel_confirmado=None,
        justificativa="Discriminador de dor toracica.",
        discriminadores_ativados=["avaliar_dor_toracica"],
        confianca=1.0,
        origem=OrigemClassificacao.REGRAS,
        confirmado_em=None,
        usado_em_treino=False,
    )


@pytest.mark.asyncio
async def test_criar_triagem_retorna_id(db_session: AsyncSession) -> None:
    profissional, paciente = await _criar_profissional_e_paciente(db_session)
    repository = TriagemRepository()
    triagem = _nova_triagem(paciente, profissional)

    resultado = await repository.criar(db_session, triagem)

    assert resultado.id is not None


@pytest.mark.asyncio
async def test_confirmar_triagem_atualiza_nivel(db_session: AsyncSession) -> None:
    profissional, paciente = await _criar_profissional_e_paciente(db_session)
    repository = TriagemRepository()
    triagem = await repository.criar(db_session, _nova_triagem(paciente, profissional))

    atualizada = await repository.confirmar(db_session, triagem.id, RiscoNivel.VERMELHO)

    assert atualizada is not None
    assert atualizada.nivel_confirmado == RiscoNivel.VERMELHO
    assert atualizada.confirmado_em is not None


@pytest.mark.asyncio
async def test_buscar_triagem_inexistente_retorna_none(db_session: AsyncSession) -> None:
    repository = TriagemRepository()

    resultado = await repository.buscar_por_id(db_session, uuid.UUID("00000000-0000-0000-0000-000000000001"))

    assert resultado is None


def test_triagem_sem_delete() -> None:
    repository = TriagemRepository()

    assert not hasattr(repository, "delete")
