"""Dependency providers for FastAPI."""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.logging_config import bind_log_context
from backend.app.core.security import decodificar_token
from backend.app.db.session import get_db as session_get_db
from backend.app.models.profissional import Profissional
from backend.app.repositories.audit_repository import AuditRepository
from backend.app.repositories.paciente_repository import PacienteRepository
from backend.app.repositories.profissional_repository import ProfissionalRepository
from backend.app.repositories.triagem_repository import TriagemRepository
from backend.app.services.auth_service import AuthService
from backend.app.services.classification import Classifier, ManchesterStrategy
from backend.app.services.triagem_service import TriagemService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncSession:
    """Yield the shared database dependency."""
    async for session in session_get_db():
        yield session


def get_profissional_repository() -> ProfissionalRepository:
    """Provide the professional repository."""
    return ProfissionalRepository()


def get_paciente_repository() -> PacienteRepository:
    """Provide the patient repository."""
    return PacienteRepository()


def get_triagem_repository() -> TriagemRepository:
    """Provide the triage repository."""
    return TriagemRepository()


def get_audit_repository() -> AuditRepository:
    """Provide the audit repository."""
    return AuditRepository()


async def get_profissional_atual(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    repo: ProfissionalRepository = Depends(get_profissional_repository),
) -> Profissional:
    """Resolve the authenticated professional."""
    payload = decodificar_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        profissional_id = uuid.UUID(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    profissional = await repo.buscar_por_id(db, profissional_id)
    if profissional is None or not profissional.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Profissional invalido ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    bind_log_context(profissional_id=str(profissional.id))
    return profissional


def get_classifier() -> Classifier:
    """Provide the default classifier implementation."""
    return Classifier(ManchesterStrategy())


def get_triagem_service(
    triagem_repo: TriagemRepository = Depends(get_triagem_repository),
    paciente_repo: PacienteRepository = Depends(get_paciente_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    classifier: Classifier = Depends(get_classifier),
    db: AsyncSession = Depends(get_db),
) -> TriagemService:
    """Compose the triage service."""
    return TriagemService(
        triagem_repo=triagem_repo,
        paciente_repo=paciente_repo,
        audit_repo=audit_repo,
        classifier=classifier,
        db=db,
    )


def get_auth_service(
    repo: ProfissionalRepository = Depends(get_profissional_repository),
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    """Compose the auth service."""
    return AuthService(repo=repo, db=db)
