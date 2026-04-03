from __future__ import annotations

import pytest

from backend.app.models.profissional import CargoProfissional
from backend.app.repositories.triagem_repository import TriagemRepository
from backend.app.services.classification import RiscoNivel


@pytest.mark.integration
@pytest.mark.asyncio
async def test_criar_triagem_retorna_model_com_id_gerado(db, paciente_factory, profissional_factory, triagem_factory) -> None:
    profissional = await profissional_factory(cargo=CargoProfissional.MEDICO)
    paciente = await paciente_factory()
    triagem = await triagem_factory(paciente_id=paciente.id, profissional_id=profissional.id)
    assert triagem.id is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_buscar_triagem_existente_retorna_model(db, paciente_factory, profissional_factory, triagem_factory) -> None:
    repo = TriagemRepository()
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    triagem = await triagem_factory(paciente_id=paciente.id, profissional_id=profissional.id)
    resultado = await repo.buscar_por_id(db, triagem.id)
    assert resultado is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_buscar_triagem_inexistente_retorna_none(db) -> None:
    resultado = await TriagemRepository().buscar_por_id(db, __import__("uuid").uuid4())
    assert resultado is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_confirmar_triagem_atualiza_nivel_confirmado_e_timestamp(db, paciente_factory, profissional_factory, triagem_factory) -> None:
    repo = TriagemRepository()
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    triagem = await triagem_factory(paciente_id=paciente.id, profissional_id=profissional.id)
    resultado = await repo.confirmar(db, triagem.id, RiscoNivel.VERMELHO)
    assert resultado is not None and resultado.confirmado_em is not None and resultado.nivel_confirmado is RiscoNivel.VERMELHO


@pytest.mark.integration
@pytest.mark.asyncio
async def test_confirmar_triagem_inexistente_retorna_none(db) -> None:
    resultado = await TriagemRepository().confirmar(db, __import__("uuid").uuid4(), RiscoNivel.AMARELO)
    assert resultado is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_listar_por_paciente_retorna_apenas_triagens_do_paciente(db, paciente_factory, profissional_factory, triagem_factory) -> None:
    repo = TriagemRepository()
    profissional = await profissional_factory()
    paciente_a = await paciente_factory(nome="Paciente A")
    paciente_b = await paciente_factory(nome="Paciente B")
    await triagem_factory(paciente_id=paciente_a.id, profissional_id=profissional.id)
    await triagem_factory(paciente_id=paciente_b.id, profissional_id=profissional.id)
    resultado = await repo.listar_por_paciente(db, paciente_a.id)
    assert len(resultado) == 1


@pytest.mark.unit
def test_triagem_repository_nao_tem_metodo_delete() -> None:
    assert not hasattr(TriagemRepository, "deletar")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_marcar_usado_em_treino_atualiza_flag(db, paciente_factory, profissional_factory, triagem_factory) -> None:
    repo = TriagemRepository()
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    triagem = await triagem_factory(paciente_id=paciente.id, profissional_id=profissional.id)
    await repo.marcar_usado_em_treino(db, triagem.id)
    atualizada = await repo.buscar_por_id(db, triagem.id)
    assert atualizada is not None and atualizada.usado_em_treino is True
