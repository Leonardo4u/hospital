from __future__ import annotations

import pytest

from backend.app.services.classification.rules.discriminators import (
    avaliar_choque,
    avaliar_comprometimento_via_aerea,
    avaliar_dor_toracica,
    avaliar_febre_alta,
    avaliar_sem_queixa_aguda,
)
from backend.app.services.classification.types import EntradaClassificacao, RiscoNivel, SinaisVitais, Sintoma


@pytest.fixture
def sinais_normais() -> SinaisVitais:
    return SinaisVitais(75, 120, 80, 98.0, 36.5, 16, 15)


def _entrada(sinais: SinaisVitais, sintomas: list[Sintoma] | None = None) -> EntradaClassificacao:
    return EntradaClassificacao(
        sinais_vitais=sinais,
        sintomas=sintomas or [],
        idade_anos=40,
        queixa_principal="avaliacao",
    )


@pytest.mark.unit
def test_glasgow_7_ativa_vermelho(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_comprometimento_via_aerea(
        _entrada(SinaisVitais(75, 120, 80, 98.0, 36.5, 16, 7))
    )
    assert resultado is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_glasgow_8_nao_ativa_via_aerea(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_comprometimento_via_aerea(
        _entrada(SinaisVitais(75, 120, 80, 98.0, 36.5, 16, 8))
    )
    assert resultado is None


@pytest.mark.unit
def test_glasgow_9_nao_ativa(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_comprometimento_via_aerea(
        _entrada(SinaisVitais(75, 120, 80, 98.0, 36.5, 16, 9))
    )
    assert resultado is None


@pytest.mark.unit
def test_spo2_84_ativa_vermelho(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_comprometimento_via_aerea(
        _entrada(SinaisVitais(75, 120, 80, 84.0, 36.5, 16, 15))
    )
    assert resultado is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_spo2_85_nao_ativa_via_aerea(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_comprometimento_via_aerea(
        _entrada(SinaisVitais(75, 120, 80, 85.0, 36.5, 16, 15))
    )
    assert resultado is None


@pytest.mark.unit
def test_spo2_86_nao_ativa_via_aerea(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_comprometimento_via_aerea(
        _entrada(SinaisVitais(75, 120, 80, 86.0, 36.5, 16, 15))
    )
    assert resultado is None


@pytest.mark.unit
def test_pas_79_ativa_vermelho(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_choque(_entrada(SinaisVitais(75, 79, 50, 98.0, 36.5, 16, 15)))
    assert resultado is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_pas_80_nao_ativa_choque(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_choque(_entrada(SinaisVitais(75, 80, 50, 98.0, 36.5, 16, 15)))
    assert resultado is None


@pytest.mark.unit
def test_fc_151_com_pas_89_ativa_vermelho(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_choque(_entrada(SinaisVitais(151, 89, 50, 98.0, 36.5, 16, 15)))
    assert resultado is RiscoNivel.VERMELHO


@pytest.mark.unit
def test_fc_149_com_pas_89_nao_ativa_choque(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_choque(_entrada(SinaisVitais(149, 89, 50, 98.0, 36.5, 16, 15)))
    assert resultado is None


@pytest.mark.unit
def test_fc_150_com_pas_90_nao_ativa_choque(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_choque(_entrada(SinaisVitais(150, 90, 50, 98.0, 36.5, 16, 15)))
    assert resultado is None


@pytest.mark.unit
def test_sintoma_dor_toracica_com_fc_101_ativa_laranja(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_dor_toracica(
        _entrada(
            SinaisVitais(101, 120, 80, 98.0, 36.5, 16, 15),
            [Sintoma("dor_toracica", "Dor toracica", 0.9)],
        )
    )
    assert resultado is RiscoNivel.LARANJA


@pytest.mark.unit
def test_sintoma_dor_toracica_sem_taquicardia_nao_ativa(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_dor_toracica(
        _entrada(sinais_normais, [Sintoma("dor_toracica", "Dor toracica", 0.9)])
    )
    assert resultado is None


@pytest.mark.unit
def test_taquicardia_sem_sintoma_dor_toracica_nao_ativa(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_dor_toracica(_entrada(SinaisVitais(110, 120, 80, 98.0, 36.5, 16, 15)))
    assert resultado is None


@pytest.mark.unit
def test_temperatura_39_5_ativa_amarelo(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_febre_alta(_entrada(SinaisVitais(75, 120, 80, 98.0, 39.5, 16, 15)))
    assert resultado is RiscoNivel.AMARELO


@pytest.mark.unit
def test_temperatura_39_4_nao_ativa_febre_alta(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_febre_alta(_entrada(SinaisVitais(75, 120, 80, 98.0, 39.4, 16, 15)))
    assert resultado is None


@pytest.mark.unit
def test_temperatura_41_ativa_amarelo(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_febre_alta(_entrada(SinaisVitais(75, 120, 80, 98.0, 41.0, 16, 15)))
    assert resultado is RiscoNivel.AMARELO


@pytest.mark.unit
def test_sem_sintomas_glasgow_15_ativa_azul(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_sem_queixa_aguda(_entrada(sinais_normais))
    assert resultado is RiscoNivel.AZUL


@pytest.mark.unit
def test_sem_sintomas_glasgow_14_nao_ativa_azul(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_sem_queixa_aguda(_entrada(SinaisVitais(75, 120, 80, 98.0, 36.5, 16, 14)))
    assert resultado is None


@pytest.mark.unit
def test_com_sintomas_glasgow_15_nao_ativa_azul(sinais_normais: SinaisVitais) -> None:
    resultado = avaliar_sem_queixa_aguda(
        _entrada(sinais_normais, [Sintoma("dor_garganta", "Dor de garganta", 0.2)])
    )
    assert resultado is None
