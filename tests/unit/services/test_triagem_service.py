from __future__ import annotations

import uuid
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from backend.app.models.profissional import CargoProfissional
from backend.app.schemas.triagem import ConfirmacaoIn, SintomaIn, SinaisVitaisIn, TriagemCreate
from backend.app.services.classification import RiscoNivel
from backend.app.services.classification.types import ResultadoClassificacao
from backend.app.services.triagem_service import TriagemService


def _dados_triagem() -> TriagemCreate:
    return TriagemCreate(
        paciente_id=uuid.uuid4(),
        sinais_vitais=SinaisVitaisIn(
            frequencia_cardiaca=80,
            pressao_sistolica=120,
            pressao_diastolica=80,
            saturacao_o2=98.0,
            temperatura=36.5,
            frequencia_respiratoria=16,
            glasgow=15,
        ),
        sintomas=[SintomaIn(codigo="dor_garganta", descricao="Dor de garganta", peso=0.2)],
        queixa_principal="Dor leve de garganta",
    )


def _resultado() -> ResultadoClassificacao:
    return ResultadoClassificacao(RiscoNivel.VERDE, "Justificativa", ["avaliar_sintomas_leves"], 1.0, "regras")


def _sinais_vitais_dict() -> dict[str, int | float]:
    return {
        "frequencia_cardiaca": 80,
        "pressao_sistolica": 120,
        "pressao_diastolica": 80,
        "saturacao_o2": 98.0,
        "temperatura": 36.5,
        "frequencia_respiratoria": 16,
        "glasgow": 15,
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classificar_verifica_existencia_do_paciente() -> None:
    paciente_repo = AsyncMock()
    paciente_repo.buscar_por_id.return_value = None
    service = TriagemService(AsyncMock(), paciente_repo, AsyncMock(), Mock(), AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await service.classificar(_dados_triagem(), uuid.uuid4(), "127.0.0.1")
    assert exc.value.status_code == 404


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classificar_chama_classifier_com_entrada_correta() -> None:
    paciente_repo = AsyncMock()
    paciente_repo.buscar_por_id.return_value = SimpleNamespace(data_nascimento=date(1990, 1, 1))
    triagem_repo = AsyncMock()
    triagem_repo.criar.return_value = SimpleNamespace(id=uuid.uuid4(), criado_em=datetime.now())
    classifier = Mock()
    classifier.classificar.return_value = _resultado()
    service = TriagemService(triagem_repo, paciente_repo, AsyncMock(), classifier, AsyncMock())
    dados = _dados_triagem()
    await service.classificar(dados, uuid.uuid4(), "127.0.0.1")
    entrada = classifier.classificar.call_args.args[0]
    assert entrada.sinais_vitais.frequencia_cardiaca == 80


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classificar_persiste_triagem() -> None:
    paciente_repo = AsyncMock()
    paciente_repo.buscar_por_id.return_value = SimpleNamespace(data_nascimento=date(1990, 1, 1))
    triagem_repo = AsyncMock()
    triagem_repo.criar.return_value = SimpleNamespace(id=uuid.uuid4(), criado_em=datetime.now())
    classifier = Mock()
    classifier.classificar.return_value = _resultado()
    service = TriagemService(triagem_repo, paciente_repo, AsyncMock(), classifier, AsyncMock())
    await service.classificar(_dados_triagem(), uuid.uuid4(), "127.0.0.1")
    triagem_repo.criar.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classificar_registra_audit_log() -> None:
    paciente_repo = AsyncMock()
    paciente_repo.buscar_por_id.return_value = SimpleNamespace(data_nascimento=date(1990, 1, 1))
    triagem_repo = AsyncMock()
    triagem_repo.criar.return_value = SimpleNamespace(id=uuid.uuid4(), criado_em=datetime.now())
    audit_repo = AsyncMock()
    classifier = Mock()
    classifier.classificar.return_value = _resultado()
    service = TriagemService(triagem_repo, paciente_repo, audit_repo, classifier, AsyncMock())
    await service.classificar(_dados_triagem(), uuid.uuid4(), "127.0.0.1")
    assert audit_repo.registrar.await_args.kwargs["acao"] == "classificar"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classificar_retorna_apenas_id_e_criado_em() -> None:
    paciente_repo = AsyncMock()
    paciente_repo.buscar_por_id.return_value = SimpleNamespace(data_nascimento=date(1990, 1, 1))
    criado_em = datetime.now()
    triagem_repo = AsyncMock()
    triagem_repo.criar.return_value = SimpleNamespace(id=uuid.uuid4(), criado_em=criado_em)
    classifier = Mock()
    classifier.classificar.return_value = _resultado()
    service = TriagemService(triagem_repo, paciente_repo, AsyncMock(), classifier, AsyncMock())
    resultado = await service.classificar(_dados_triagem(), uuid.uuid4(), "127.0.0.1")
    assert set(resultado.model_dump().keys()) == {"id", "criado_em"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_confirmar_triagem_ja_confirmada_retorna_409() -> None:
    triagem = SimpleNamespace(nivel_confirmado=RiscoNivel.AMARELO)
    triagem_repo = AsyncMock()
    triagem_repo.buscar_por_id.return_value = triagem
    service = TriagemService(triagem_repo, AsyncMock(), AsyncMock(), Mock(), AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await service.confirmar(
            uuid.uuid4(),
            ConfirmacaoIn(nivel_confirmado=RiscoNivel.AMARELO),
            uuid.uuid4(),
            CargoProfissional.MEDICO,
            "127.0.0.1",
        )
    assert exc.value.status_code == 409


@pytest.mark.unit
@pytest.mark.asyncio
async def test_confirmar_registra_audit_correcao_quando_nivel_diverge() -> None:
    triagem = SimpleNamespace(id=uuid.uuid4(), nivel_confirmado=None, nivel_calculado=RiscoNivel.VERDE)
    triagem_atualizada = SimpleNamespace(
        id=triagem.id,
        paciente_id=uuid.uuid4(),
        profissional_id=uuid.uuid4(),
        sinais_vitais=_sinais_vitais_dict(),
        sintomas=[],
        queixa_principal="q",
        nivel_calculado=RiscoNivel.VERDE,
        nivel_confirmado=RiscoNivel.AMARELO,
        justificativa="j",
        discriminadores_ativados=[],
        confianca=1.0,
        origem=SimpleNamespace(value="regras"),
        confirmado_em=datetime.now(),
        usado_em_treino=False,
        criado_em=datetime.now(),
        atualizado_em=datetime.now(),
    )
    triagem_repo = AsyncMock()
    triagem_repo.buscar_por_id.return_value = triagem
    triagem_repo.confirmar.return_value = triagem_atualizada
    audit_repo = AsyncMock()
    service = TriagemService(triagem_repo, AsyncMock(), audit_repo, Mock(), AsyncMock())
    await service.confirmar(
        uuid.uuid4(),
        ConfirmacaoIn(nivel_confirmado=RiscoNivel.AMARELO),
        uuid.uuid4(),
        CargoProfissional.MEDICO,
        "127.0.0.1",
    )
    assert audit_repo.registrar.await_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_confirmar_nao_registra_correcao_quando_nivel_igual() -> None:
    triagem = SimpleNamespace(id=uuid.uuid4(), nivel_confirmado=None, nivel_calculado=RiscoNivel.AMARELO)
    triagem_atualizada = SimpleNamespace(
        id=triagem.id,
        paciente_id=uuid.uuid4(),
        profissional_id=uuid.uuid4(),
        sinais_vitais=_sinais_vitais_dict(),
        sintomas=[],
        queixa_principal="q",
        nivel_calculado=RiscoNivel.AMARELO,
        nivel_confirmado=RiscoNivel.AMARELO,
        justificativa="j",
        discriminadores_ativados=[],
        confianca=1.0,
        origem=SimpleNamespace(value="regras"),
        confirmado_em=datetime.now(),
        usado_em_treino=False,
        criado_em=datetime.now(),
        atualizado_em=datetime.now(),
    )
    triagem_repo = AsyncMock()
    triagem_repo.buscar_por_id.return_value = triagem
    triagem_repo.confirmar.return_value = triagem_atualizada
    audit_repo = AsyncMock()
    service = TriagemService(triagem_repo, AsyncMock(), audit_repo, Mock(), AsyncMock())
    await service.confirmar(
        uuid.uuid4(),
        ConfirmacaoIn(nivel_confirmado=RiscoNivel.AMARELO),
        uuid.uuid4(),
        CargoProfissional.MEDICO,
        "127.0.0.1",
    )
    assert audit_repo.registrar.await_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_confirmar_bloqueia_tecnico_com_403() -> None:
    service = TriagemService(AsyncMock(), AsyncMock(), AsyncMock(), Mock(), AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await service.confirmar(
            uuid.uuid4(),
            ConfirmacaoIn(nivel_confirmado=RiscoNivel.AMARELO),
            uuid.uuid4(),
            CargoProfissional.TECNICO,
            "127.0.0.1",
        )
    assert exc.value.status_code == 403


@pytest.mark.unit
@pytest.mark.asyncio
async def test_confirmar_bloqueia_enfermeiro_para_laranja_e_vermelho() -> None:
    service = TriagemService(AsyncMock(), AsyncMock(), AsyncMock(), Mock(), AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await service.confirmar(
            uuid.uuid4(),
            ConfirmacaoIn(nivel_confirmado=RiscoNivel.LARANJA),
            uuid.uuid4(),
            CargoProfissional.ENFERMEIRO,
            "127.0.0.1",
        )
    assert exc.value.status_code == 403
