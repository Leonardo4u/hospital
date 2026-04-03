"""Unit tests for the Manchester engine."""

from __future__ import annotations

import pytest

from backend.app.services.classification.rules.manchester_engine import ManchesterEngine
from backend.app.services.classification.types import (
    EntradaClassificacao,
    RiscoNivel,
    SinaisVitais,
    Sintoma,
)


def _entrada_base(**sinais_overrides: int | float) -> EntradaClassificacao:
    sinais_padrao: dict[str, int | float] = {
        "frequencia_cardiaca": 80,
        "pressao_sistolica": 120,
        "pressao_diastolica": 80,
        "saturacao_o2": 98.0,
        "temperatura": 36.8,
        "frequencia_respiratoria": 16,
        "glasgow": 15,
    }
    sinais_padrao.update(sinais_overrides)
    return EntradaClassificacao(
        sinais_vitais=SinaisVitais(**sinais_padrao),
        sintomas=[Sintoma(codigo="mal_estar", descricao="Mal-estar geral", peso=0.2)],
        idade_anos=42,
        queixa_principal="Avaliacao clinica",
    )


def test_choque_ativa_vermelho() -> None:
    engine = ManchesterEngine()
    entrada = _entrada_base(frequencia_cardiaca=160, pressao_sistolica=85)

    resultado = engine.classificar(entrada)

    assert resultado.nivel is RiscoNivel.VERMELHO


def test_glasgow_baixo_ativa_vermelho() -> None:
    engine = ManchesterEngine()
    entrada = _entrada_base(glasgow=6)

    resultado = engine.classificar(entrada)

    assert resultado.nivel is RiscoNivel.VERMELHO


def test_febre_alta_ativa_amarelo() -> None:
    engine = ManchesterEngine()
    entrada = _entrada_base(temperatura=40.0)

    resultado = engine.classificar(entrada)

    assert resultado.nivel is RiscoNivel.AMARELO


def test_entrada_invalida_lanca_valueerror() -> None:
    with pytest.raises(ValueError, match="frequencia_cardiaca fora do intervalo fisiologico valido"):
        _entrada_base(frequencia_cardiaca=-1)


def test_paciente_sem_queixa_ativa_azul() -> None:
    engine = ManchesterEngine()
    entrada = EntradaClassificacao(
        sinais_vitais=SinaisVitais(
            frequencia_cardiaca=72,
            pressao_sistolica=118,
            pressao_diastolica=76,
            saturacao_o2=99.0,
            temperatura=36.5,
            frequencia_respiratoria=14,
            glasgow=15,
        ),
        sintomas=[],
        idade_anos=30,
        queixa_principal="Check-up",
    )

    resultado = engine.classificar(entrada)

    assert resultado.nivel is RiscoNivel.AZUL


def test_discriminador_mais_grave_prevalece() -> None:
    engine = ManchesterEngine()
    entrada = _entrada_base(temperatura=40.0, glasgow=7)

    resultado = engine.classificar(entrada)

    assert resultado.nivel is RiscoNivel.VERMELHO
