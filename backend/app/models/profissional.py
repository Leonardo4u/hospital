"""ORM model for healthcare professionals."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class CargoProfissional(str, Enum):
    """Supported professional roles."""

    MEDICO = "MEDICO"
    ENFERMEIRO = "ENFERMEIRO"
    TECNICO = "TECNICO"


class Profissional(Base):
    """Healthcare professional persistence model."""

    __tablename__ = "profissionais"

    nome: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    crm: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True)
    cargo: Mapped[CargoProfissional] = mapped_column(
        SqlEnum(CargoProfissional, name="cargo_profissional", native_enum=False),
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(nullable=False, default=True, server_default=text("true"))
