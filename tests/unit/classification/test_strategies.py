from __future__ import annotations

from dataclasses import replace
from unittest.mock import Mock

import pytest

from backend.app.services.classification import Classifier, EntradaClassificacao, RiscoNivel, SinaisVitais
from backend.app.services.classification.rules.manchester_engine import ManchesterEngine
from backend.app.services.classification.strategies import HybridStrategy, MLStrategy, ManchesterStrategy
from backend.app.services.classification.types import ResultadoClassificacao


def _entrada() -> EntradaClassificacao:
    return EntradaClassificacao(
        sinais_vitais=SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 15),
        sintomas=[],
        idade_anos=30,
        queixa_principal="avaliacao",
    )


@pytest.mark.unit
def test_manchester_strategy_delega_para_engine() -> None:
    engine = Mock(spec=ManchesterEngine)
    engine.classificar.return_value = ResultadoClassificacao(RiscoNivel.AZUL, "ok", [], 1.0, "regras")
    resultado = ManchesterStrategy(engine).classificar(_entrada())
    assert resultado.nivel is RiscoNivel.AZUL


@pytest.mark.unit
def test_ml_strategy_levanta_not_implemented_error() -> None:
    with pytest.raises(NotImplementedError):
        MLStrategy().classificar(_entrada())


@pytest.mark.unit
def test_hybrid_strategy_retorna_manchester_quando_ml_falha() -> None:
    manchester = Mock()
    manchester.classificar.return_value = ResultadoClassificacao(RiscoNivel.AMARELO, "ok", [], 1.0, "regras")
    ml = Mock()
    ml.classificar.side_effect = NotImplementedError
    resultado = HybridStrategy(manchester, ml).classificar(_entrada())
    assert resultado.origem == "regras"


@pytest.mark.unit
def test_hybrid_strategy_retorna_hibrido_quando_ambos_concordam() -> None:
    manchester_resultado = ResultadoClassificacao(RiscoNivel.AMARELO, "ok", [], 1.0, "regras")
    manchester = Mock()
    manchester.classificar.return_value = manchester_resultado
    ml = Mock()
    ml.classificar.return_value = replace(manchester_resultado, origem="ml")
    resultado = HybridStrategy(manchester, ml).classificar(_entrada())
    assert resultado.origem == "hibrido"


@pytest.mark.unit
def test_classifier_recusa_entrada_none() -> None:
    strategy = Mock()
    with pytest.raises(ValueError):
        Classifier(strategy).classificar(None)  # type: ignore[arg-type]


@pytest.mark.unit
def test_classifier_delega_para_strategy_injetada() -> None:
    strategy = Mock()
    strategy.classificar.return_value = ResultadoClassificacao(RiscoNivel.AZUL, "ok", [], 1.0, "regras")
    entrada = _entrada()
    Classifier(strategy).classificar(entrada)
    strategy.classificar.assert_called_once_with(entrada)
