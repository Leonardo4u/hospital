from __future__ import annotations

import uuid

import pytest

from backend.app.repositories.audit_repository import AuditRepository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_registrar_cria_registro_imutavel(db, profissional_factory) -> None:
    profissional = await profissional_factory()
    registro = await AuditRepository().registrar(
        db,
        "triagem",
        uuid.uuid4(),
        "classificar",
        profissional.id,
        None,
        {"nivel": "amarelo"},
        "127.0.0.1",
    )
    assert registro.id is not None


@pytest.mark.unit
def test_audit_repository_nao_tem_metodo_update() -> None:
    assert not hasattr(AuditRepository, "atualizar")


@pytest.mark.unit
def test_audit_repository_nao_tem_metodo_delete() -> None:
    assert not hasattr(AuditRepository, "deletar")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_registrar_com_payload_none_aceito(db, profissional_factory) -> None:
    profissional = await profissional_factory()
    registro = await AuditRepository().registrar(
        db,
        "triagem",
        uuid.uuid4(),
        "confirmar",
        profissional.id,
        None,
        None,
        None,
    )
    assert registro.payload_depois is None
