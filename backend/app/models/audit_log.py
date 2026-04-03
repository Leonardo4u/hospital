"""ORM model for immutable audit entries."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class AuditLog(Base):
    """Immutable audit log persistence model."""

    __tablename__ = "audit_logs"

    entidade: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entidade_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    acao: Mapped[str] = mapped_column(String(64), nullable=False)
    profissional_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profissionais.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payload_antes: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON, nullable=True)
    payload_depois: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON, nullable=True)
    ip_origem: Mapped[str | None] = mapped_column(Text, nullable=True)
