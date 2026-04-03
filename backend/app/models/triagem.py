"""ORM model for triage records."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Enum as SqlEnum, Float, ForeignKey, JSON, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.services.classification.types import RiscoNivel


class OrigemClassificacao(str, Enum):
    """Supported classification origins."""

    REGRAS = "regras"
    ML = "ml"
    HIBRIDO = "hibrido"


class Triagem(Base):
    """Triage persistence model."""

    __tablename__ = "triagens"

    paciente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pacientes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    profissional_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profissionais.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sinais_vitais: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    sintomas: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    queixa_principal: Mapped[str] = mapped_column(Text, nullable=False)
    nivel_calculado: Mapped[RiscoNivel] = mapped_column(
        SqlEnum(RiscoNivel, name="risco_nivel", native_enum=False),
        nullable=False,
    )
    nivel_confirmado: Mapped[RiscoNivel | None] = mapped_column(
        SqlEnum(RiscoNivel, name="risco_nivel_confirmado", native_enum=False),
        nullable=True,
    )
    justificativa: Mapped[str] = mapped_column(Text, nullable=False)
    discriminadores_ativados: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    confianca: Mapped[float] = mapped_column(Float, nullable=False)
    origem: Mapped[OrigemClassificacao] = mapped_column(
        SqlEnum(OrigemClassificacao, name="origem_classificacao", native_enum=False),
        nullable=False,
    )
    confirmado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usado_em_treino: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default=text("false"),
    )
