"""ORM model for patients."""

from __future__ import annotations

from datetime import date
from enum import Enum

from sqlalchemy import Date, Enum as SqlEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class SexoPaciente(str, Enum):
    """Supported patient sex values."""

    M = "M"
    F = "F"
    OUTRO = "OUTRO"


class Paciente(Base):
    """Patient persistence model."""

    __tablename__ = "pacientes"

    nome_completo: Mapped[str] = mapped_column(Text, nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(11), nullable=True, unique=True, index=True)
    sexo: Mapped[SexoPaciente] = mapped_column(
        SqlEnum(SexoPaciente, name="sexo_paciente", native_enum=False),
        nullable=False,
    )
    contato_emergencia: Mapped[str | None] = mapped_column(Text, nullable=True)
