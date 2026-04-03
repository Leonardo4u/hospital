from __future__ import annotations

import pytest

from backend.app.services.classification.rules.manchester_engine import ManchesterEngine
from backend.app.services.classification.types import EntradaClassificacao, RiscoNivel, SinaisVitais, Sintoma


def _entrada(sinais: SinaisVitais, sintomas: list[Sintoma] | None = None) -> EntradaClassificacao:
    return EntradaClassificacao(
        sinais_vitais=sinais,
        sintomas=sintomas or [],
        idade_anos=30,
        queixa_principal="avaliacao clinica",
    )


@pytest.mark.unit
def test_pcr_simulado() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(30, 90, 50, 60.0, 36.5, 28, 3))
    )
    assert resultado.nivel is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_choque_hipovolemico() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(160, 75, 50, 94.0, 36.5, 20, 14))
    )
    assert resultado.nivel is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_glasgow_critico_isolado() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 6))
    )
    assert resultado.nivel is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_dor_toracica_com_taquicardia() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(
            SinaisVitais(110, 120, 80, 98.0, 36.5, 16, 15),
            [Sintoma("dor_toracica", "Dor toracica", 0.9)],
        )
    )
    assert resultado.nivel is RiscoNivel.LARANJA


@pytest.mark.unit
def test_alteracao_consciencia() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 10))
    )
    assert resultado.nivel is RiscoNivel.LARANJA


@pytest.mark.unit
def test_febre_alta_isolada() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(95, 125, 82, 96.0, 40.0, 20, 15))
    )
    assert resultado.nivel is RiscoNivel.AMARELO


@pytest.mark.unit
def test_hipertensao_grave() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(80, 185, 95, 98.0, 36.5, 16, 15))
    )
    assert resultado.nivel is RiscoNivel.AMARELO


@pytest.mark.unit
def test_saturacao_limiar() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(80, 120, 80, 90.0, 36.5, 16, 15))
    )
    assert resultado.nivel is RiscoNivel.AMARELO


@pytest.mark.unit
def test_sintoma_leve_sem_alteracoes() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(
            SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 15),
            [Sintoma("dor_garganta", "Dor de garganta", 0.2)],
        )
    )
    assert resultado.nivel is RiscoNivel.VERDE


@pytest.mark.unit
def test_consulta_de_rotina() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(68, 118, 76, 99.0, 36.2, 14, 15))
    )
    assert resultado.nivel is RiscoNivel.AZUL


@pytest.mark.unit
def test_febre_mais_glasgow_critico_retorna_vermelho_nao_amarelo() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(95, 125, 82, 96.0, 40.0, 20, 7))
    )
    assert resultado.nivel is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_dois_discriminadores_laranja_retorna_laranja() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(
            SinaisVitais(110, 120, 80, 98.0, 36.5, 16, 10),
            [Sintoma("dor_toracica", "Dor toracica", 0.9)],
        )
    )
    assert resultado.nivel is RiscoNivel.LARANJA


@pytest.mark.unit
def test_discriminadores_ativados_listados_no_resultado() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(
            SinaisVitais(110, 120, 80, 98.0, 36.5, 16, 10),
            [Sintoma("dor_toracica", "Dor toracica", 0.9)],
        )
    )
    assert "avaliar_dor_toracica" in resultado.discriminadores_ativados


@pytest.mark.unit
def test_justificativa_nao_vazia() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(95, 125, 82, 96.0, 40.0, 20, 15))
    )
    assert len(resultado.justificativa) > 0


@pytest.mark.unit
def test_confianca_e_1_0_no_motor_de_regras() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(95, 125, 82, 96.0, 40.0, 20, 15))
    )
    assert resultado.confianca == 1.0


@pytest.mark.unit
def test_origem_e_regras() -> None:
    resultado = ManchesterEngine().classificar(
        _entrada(SinaisVitais(95, 125, 82, 96.0, 40.0, 20, 15))
    )
    assert resultado.origem == "regras"
