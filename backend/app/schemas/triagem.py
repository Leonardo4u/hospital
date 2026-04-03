"""Pydantic schemas for triage requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.services.classification.types import RiscoNivel


class SinaisVitaisIn(BaseModel):
    """Validated triage vital signs."""

    frequencia_cardiaca: int
    pressao_sistolica: int
    pressao_diastolica: int
    saturacao_o2: float
    temperatura: float
    frequencia_respiratoria: int
    glasgow: int

    @field_validator("frequencia_cardiaca")
    @classmethod
    def validar_frequencia_cardiaca(cls, value: int) -> int:
        """Validate heart rate."""
        if not 20 <= value <= 300:
            raise ValueError("frequencia_cardiaca deve estar entre 20 e 300 bpm.")
        return value

    @field_validator("pressao_sistolica")
    @classmethod
    def validar_pressao_sistolica(cls, value: int) -> int:
        """Validate systolic pressure."""
        if not 40 <= value <= 300:
            raise ValueError("pressao_sistolica deve estar entre 40 e 300 mmHg.")
        return value

    @field_validator("pressao_diastolica")
    @classmethod
    def validar_pressao_diastolica(cls, value: int) -> int:
        """Validate diastolic pressure."""
        if not 20 <= value <= 200:
            raise ValueError("pressao_diastolica deve estar entre 20 e 200 mmHg.")
        return value

    @field_validator("saturacao_o2")
    @classmethod
    def validar_saturacao(cls, value: float) -> float:
        """Validate oxygen saturation."""
        if not 50.0 <= value <= 100.0:
            raise ValueError("saturacao_o2 deve estar entre 50.0 e 100.0.")
        return value

    @field_validator("temperatura")
    @classmethod
    def validar_temperatura(cls, value: float) -> float:
        """Validate temperature."""
        if not 28.0 <= value <= 45.0:
            raise ValueError("temperatura deve estar entre 28.0 e 45.0 C.")
        return value

    @field_validator("frequencia_respiratoria")
    @classmethod
    def validar_frequencia_respiratoria(cls, value: int) -> int:
        """Validate respiratory rate."""
        if not 4 <= value <= 60:
            raise ValueError("frequencia_respiratoria deve estar entre 4 e 60 irpm.")
        return value

    @field_validator("glasgow")
    @classmethod
    def validar_glasgow(cls, value: int) -> int:
        """Validate Glasgow score."""
        if not 3 <= value <= 15:
            raise ValueError("glasgow deve estar entre 3 e 15.")
        return value


class SintomaIn(BaseModel):
    """Validated triage symptom."""

    codigo: str
    descricao: str
    peso: float = Field(ge=0.0, le=1.0)


class TriagemCreate(BaseModel):
    """Input schema for triage creation."""

    paciente_id: uuid.UUID
    sinais_vitais: SinaisVitaisIn
    sintomas: list[SintomaIn]
    queixa_principal: str = Field(min_length=3)


class TriagemCreatedOut(BaseModel):
    """Output schema for triage write operations."""

    id: uuid.UUID
    criado_em: datetime


class TriagemOut(BaseModel):
    """Output schema for triage reads."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    paciente_id: uuid.UUID
    profissional_id: uuid.UUID
    sinais_vitais: SinaisVitaisIn
    sintomas: list[SintomaIn]
    queixa_principal: str
    nivel_calculado: RiscoNivel
    nivel_confirmado: RiscoNivel | None
    justificativa: str
    discriminadores_ativados: list[str]
    confianca: float
    origem: Literal["regras", "ml", "hibrido"]
    confirmado_em: datetime | None
    usado_em_treino: bool
    criado_em: datetime
    atualizado_em: datetime


class ConfirmacaoIn(BaseModel):
    """Input schema for triage confirmation."""

    nivel_confirmado: RiscoNivel

    @field_validator("nivel_confirmado", mode="before")
    @classmethod
    def normalizar_nivel_confirmado(cls, value: object) -> object:
        """Normalize incoming risk level text for enum parsing."""
        if isinstance(value, str):
            return value.lower()
        return value
