"""Pydantic schemas for patients."""

from __future__ import annotations

import re
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from backend.app.models.paciente import SexoPaciente

_CPF_PATTERN = re.compile(r"\D")


class PacienteCreate(BaseModel):
    """Input schema for patient creation."""

    nome_completo: str
    data_nascimento: date
    cpf: str | None = None
    sexo: SexoPaciente
    contato_emergencia: str | None = None

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: str | None) -> str | None:
        """Normalize and validate CPF format."""
        if value is None:
            return None
        cpf_normalizado = _CPF_PATTERN.sub("", value)
        if len(cpf_normalizado) != 11 or not cpf_normalizado.isdigit():
            raise ValueError("cpf deve conter 11 digitos.")
        return cpf_normalizado


class PacienteOut(BaseModel):
    """Output schema for patients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome_completo: str
    data_nascimento: date
    cpf: str | None
    sexo: SexoPaciente
    contato_emergencia: str | None
    criado_em: datetime


class PacienteUpdate(BaseModel):
    """Input schema for patient partial updates."""

    nome_completo: str | None = None
    data_nascimento: date | None = None
    cpf: str | None = None
    sexo: SexoPaciente | None = None
    contato_emergencia: str | None = None

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, value: str | None) -> str | None:
        """Normalize and validate CPF format."""
        if value is None:
            return None
        cpf_normalizado = _CPF_PATTERN.sub("", value)
        if len(cpf_normalizado) != 11 or not cpf_normalizado.isdigit():
            raise ValueError("cpf deve conter 11 digitos.")
        return cpf_normalizado
