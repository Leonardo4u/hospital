"""Repository for immutable audit log insertion."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.audit_log import AuditLog


class AuditRepository:
    """Write-only data access for audit logs."""

    async def registrar(
        self,
        db: AsyncSession,
        entidade: str,
        entidade_id: uuid.UUID,
        acao: str,
        profissional_id: uuid.UUID,
        payload_antes: dict[str, Any] | list[Any] | None,
        payload_depois: dict[str, Any] | list[Any] | None,
        ip: str | None,
    ) -> AuditLog:
        """Insert a new audit log entry."""
        registro = AuditLog(
            entidade=entidade,
            entidade_id=entidade_id,
            acao=acao,
            profissional_id=profissional_id,
            payload_antes=payload_antes,
            payload_depois=payload_depois,
            ip_origem=ip,
        )
        db.add(registro)
        await db.commit()
        await db.refresh(registro)
        return registro
