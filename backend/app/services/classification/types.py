"""Clinical data types for classification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class RiscoNivel(Enum):
    """Manchester risk levels."""

    VERMELHO = "vermelho"
    LARANJA = "laranja"
    AMARELO = "amarelo"
    VERDE = "verde"
    AZUL = "azul"


@dataclass(frozen=True, slots=True)
class NivelInfo:
    """Presentation metadata for a risk level."""

    cor: str
    label: str
    tempo_maximo_minutos: int | None


NIVEL_INFO: dict[RiscoNivel, NivelInfo] = {
    RiscoNivel.VERMELHO: NivelInfo(cor="#FF0000", label="Emergencia", tempo_maximo_minutos=0),
    RiscoNivel.LARANJA: NivelInfo(cor="#FFA500", label="Muito urgente", tempo_maximo_minutos=10),
    RiscoNivel.AMARELO: NivelInfo(cor="#FFFF00", label="Urgente", tempo_maximo_minutos=60),
    RiscoNivel.VERDE: NivelInfo(cor="#008000", label="Pouco urgente", tempo_maximo_minutos=120),
    RiscoNivel.AZUL: NivelInfo(cor="#0000FF", label="Nao urgente", tempo_maximo_minutos=240),
}


@dataclass(slots=True)
class SinaisVitais:
    """Validated vital signs."""

    frequencia_cardiaca: int
    pressao_sistolica: int
    pressao_diastolica: int
    saturacao_o2: float
    temperatura: float
    frequencia_respiratoria: int
    glasgow: int

    def __post_init__(self) -> None:
        """Validate physiological ranges."""
        self._validar_intervalo("frequencia_cardiaca", self.frequencia_cardiaca, 20, 300, "bpm")
        self._validar_intervalo("pressao_sistolica", self.pressao_sistolica, 40, 300, "mmHg")
        self._validar_intervalo("pressao_diastolica", self.pressao_diastolica, 20, 200, "mmHg")
        self._validar_intervalo("saturacao_o2", self.saturacao_o2, 50.0, 100.0, "%")
        self._validar_intervalo("temperatura", self.temperatura, 28.0, 45.0, "C")
        self._validar_intervalo(
            "frequencia_respiratoria",
            self.frequencia_respiratoria,
            4,
            60,
            "irpm",
        )
        self._validar_intervalo("glasgow", self.glasgow, 3, 15, "pontos")

    @staticmethod
    def _validar_intervalo(
        campo: str,
        valor: int | float,
        minimo: int | float,
        maximo: int | float,
        unidade: str,
    ) -> None:
        if not minimo <= valor <= maximo:
            raise ValueError(
                f"{campo} fora do intervalo fisiologico valido: "
                f"recebido {valor}, esperado entre {minimo} e {maximo} {unidade}."
            )


@dataclass(frozen=True, slots=True)
class Sintoma:
    """Reported symptom."""

    codigo: str
    descricao: str
    peso: float


@dataclass(slots=True)
class EntradaClassificacao:
    """Input payload for clinical classification."""

    sinais_vitais: SinaisVitais
    sintomas: list[Sintoma]
    idade_anos: int
    queixa_principal: str


@dataclass(frozen=True, slots=True)
class ResultadoClassificacao:
    """Output payload for clinical classification."""

    nivel: RiscoNivel
    justificativa: str
    discriminadores_ativados: list[str]
    confianca: float
    origem: Literal["regras", "ml", "hibrido"]
