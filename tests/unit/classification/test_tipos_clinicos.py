from __future__ import annotations

import pytest

from backend.app.services.classification.types import SinaisVitais


@pytest.mark.unit
def test_sinais_vitais_validos_instancia_sem_erro() -> None:
    sinais = SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 15)
    assert sinais.glasgow == 15


@pytest.mark.unit
def test_fc_zero_levanta_valueerror() -> None:
    with pytest.raises(ValueError):
        SinaisVitais(0, 120, 80, 98.0, 36.5, 16, 15)


@pytest.mark.unit
def test_fc_negativo_levanta_valueerror() -> None:
    with pytest.raises(ValueError):
        SinaisVitais(-1, 120, 80, 98.0, 36.5, 16, 15)


@pytest.mark.unit
def test_spo2_acima_de_100_levanta_valueerror() -> None:
    with pytest.raises(ValueError):
        SinaisVitais(80, 120, 80, 101.0, 36.5, 16, 15)


@pytest.mark.unit
def test_glasgow_abaixo_de_3_levanta_valueerror() -> None:
    with pytest.raises(ValueError):
        SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 2)


@pytest.mark.unit
def test_glasgow_acima_de_15_levanta_valueerror() -> None:
    with pytest.raises(ValueError):
        SinaisVitais(80, 120, 80, 98.0, 36.5, 16, 16)


@pytest.mark.unit
def test_temperatura_hipotermia_grave_levanta_valueerror() -> None:
    with pytest.raises(ValueError):
        SinaisVitais(80, 120, 80, 98.0, 27.9, 16, 15)


@pytest.mark.unit
def test_todos_os_campos_no_limite_inferior_sao_validos() -> None:
    sinais = SinaisVitais(20, 40, 20, 50.0, 28.0, 4, 3)
    assert sinais.pressao_sistolica == 40


@pytest.mark.unit
def test_todos_os_campos_no_limite_superior_sao_validos() -> None:
    sinais = SinaisVitais(300, 300, 200, 100.0, 45.0, 60, 15)
    assert sinais.frequencia_cardiaca == 300


@pytest.mark.unit
def test_mensagem_de_erro_contem_nome_do_campo() -> None:
    with pytest.raises(ValueError, match="frequencia_cardiaca"):
        SinaisVitais(10, 120, 80, 98.0, 36.5, 16, 15)
