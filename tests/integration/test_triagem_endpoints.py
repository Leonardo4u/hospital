from __future__ import annotations

import pytest

from backend.app.models.profissional import CargoProfissional
from backend.app.models.audit_log import AuditLog
from backend.app.services.classification import RiscoNivel


@pytest.mark.integration
@pytest.mark.asyncio
async def test_post_triagem_retorna_apenas_id_e_criado_em(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    response = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_normais, "sintomas": [{"codigo": "dor_garganta", "descricao": "Dor de garganta", "peso": 0.2}], "queixa_principal": "Dor de garganta"}, headers={"Authorization": f"Bearer {token}"})
    assert set(response.json().keys()) == {"id", "criado_em"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_post_triagem_nao_retorna_nivel_calculado(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    response = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_normais, "sintomas": [{"codigo": "dor_garganta", "descricao": "Dor de garganta", "peso": 0.2}], "queixa_principal": "Dor de garganta"}, headers={"Authorization": f"Bearer {token}"})
    assert "nivel_calculado" not in response.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_triagem_retorna_resultado_completo(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_febre) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    criar = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_febre, "sintomas": [], "queixa_principal": "Febre alta"}, headers={"Authorization": f"Bearer {token}"})
    response = await client.get(f"/api/v1/triagens/{criar.json()['id']}", headers={"Authorization": f"Bearer {token}"})
    assert {"id", "nivel_calculado", "justificativa", "discriminadores_ativados", "confianca", "origem"}.issubset(response.json().keys())


@pytest.mark.integration
@pytest.mark.asyncio
async def test_glasgow_invalido_retorna_422_com_campo_identificado(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    payload = {"paciente_id": str(paciente.id), "sinais_vitais": {**sinais_vitais_normais, "glasgow": 20}, "sintomas": [], "queixa_principal": "Observacao"}
    response = await client.post("/api/v1/triagens/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422 and "glasgow" in str(response.json()["detail"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fc_negativa_retorna_422(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    payload = {"paciente_id": str(paciente.id), "sinais_vitais": {**sinais_vitais_normais, "frequencia_cardiaca": -1}, "sintomas": [], "queixa_principal": "Observacao"}
    response = await client.post("/api/v1/triagens/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spo2_acima_100_retorna_422(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    payload = {"paciente_id": str(paciente.id), "sinais_vitais": {**sinais_vitais_normais, "saturacao_o2": 101.0}, "sintomas": [], "queixa_principal": "Observacao"}
    response = await client.post("/api/v1/triagens/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_queixa_muito_curta_retorna_422(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    payload = {"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_normais, "sintomas": [], "queixa_principal": "Oi"}
    response = await client.post("/api/v1/triagens/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fluxo_completo_classificar_e_confirmar(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_febre) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    criar = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_febre, "sintomas": [], "queixa_principal": "Febre alta"}, headers={"Authorization": f"Bearer {token}"})
    triagem = await client.get(f"/api/v1/triagens/{criar.json()['id']}", headers={"Authorization": f"Bearer {token}"})
    confirmar = await client.post(f"/api/v1/triagens/{criar.json()['id']}/confirmar", json={"nivel_confirmado": triagem.json()["nivel_calculado"]}, headers={"Authorization": f"Bearer {token}"})
    assert confirmar.json()["nivel_confirmado"] == triagem.json()["nivel_calculado"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_confirmar_duas_vezes_retorna_409(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_azul) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    criar = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_azul, "sintomas": [], "queixa_principal": "Rotina"}, headers={"Authorization": f"Bearer {token}"})
    await client.post(f"/api/v1/triagens/{criar.json()['id']}/confirmar", json={"nivel_confirmado": "azul"}, headers={"Authorization": f"Bearer {token}"})
    response = await client.post(f"/api/v1/triagens/{criar.json()['id']}/confirmar", json={"nivel_confirmado": "azul"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 409


@pytest.mark.integration
@pytest.mark.asyncio
async def test_confirmar_com_nivel_diferente_aceito(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_azul) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    criar = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_azul, "sintomas": [], "queixa_principal": "Rotina"}, headers={"Authorization": f"Bearer {token}"})
    response = await client.post(f"/api/v1/triagens/{criar.json()['id']}/confirmar", json={"nivel_confirmado": RiscoNivel.VERMELHO.value}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_audit_log_criado_apos_classificacao(client, db, profissional_factory, token_factory, paciente_factory, sinais_vitais_normais) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_normais, "sintomas": [], "queixa_principal": "Rotina"}, headers={"Authorization": f"Bearer {token}"})
    quantidade = len((await db.execute(__import__("sqlalchemy").select(AuditLog))).scalars().all())
    assert quantidade == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_audit_log_criado_apos_confirmacao(client, db, profissional_factory, token_factory, paciente_factory, sinais_vitais_febre) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    criar = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_febre, "sintomas": [], "queixa_principal": "Febre"}, headers={"Authorization": f"Bearer {token}"})
    await client.post(f"/api/v1/triagens/{criar.json()['id']}/confirmar", json={"nivel_confirmado": "amarelo"}, headers={"Authorization": f"Bearer {token}"})
    quantidade = len((await db.execute(__import__("sqlalchemy").select(AuditLog))).scalars().all())
    assert quantidade == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dois_audit_logs_criados_quando_nivel_corrigido(client, db, profissional_factory, token_factory, paciente_factory, sinais_vitais_azul) -> None:
    profissional = await profissional_factory()
    paciente = await paciente_factory()
    token = token_factory(profissional)
    criar = await client.post("/api/v1/triagens/", json={"paciente_id": str(paciente.id), "sinais_vitais": sinais_vitais_azul, "sintomas": [], "queixa_principal": "Rotina"}, headers={"Authorization": f"Bearer {token}"})
    await client.post(f"/api/v1/triagens/{criar.json()['id']}/confirmar", json={"nivel_confirmado": "vermelho"}, headers={"Authorization": f"Bearer {token}"})
    quantidade = len((await db.execute(__import__("sqlalchemy").select(AuditLog))).scalars().all())
    assert quantidade == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tecnico_nao_pode_confirmar_classificacao(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_azul) -> None:
    medico = await profissional_factory(cargo=CargoProfissional.MEDICO)
    tecnico = await profissional_factory(cargo=CargoProfissional.TECNICO)
    paciente = await paciente_factory()

    token_medico = token_factory(medico)
    token_tecnico = token_factory(tecnico)

    criar = await client.post(
        "/api/v1/triagens/",
        json={
            "paciente_id": str(paciente.id),
            "sinais_vitais": sinais_vitais_azul,
            "sintomas": [],
            "queixa_principal": "Rotina",
        },
        headers={"Authorization": f"Bearer {token_medico}"},
    )

    confirmar = await client.post(
        f"/api/v1/triagens/{criar.json()['id']}/confirmar",
        json={"nivel_confirmado": "azul"},
        headers={"Authorization": f"Bearer {token_tecnico}"},
    )

    assert confirmar.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_enfermeiro_nao_pode_confirmar_laranja_ou_vermelho(client, profissional_factory, token_factory, paciente_factory, sinais_vitais_azul) -> None:
    medico = await profissional_factory(cargo=CargoProfissional.MEDICO)
    enfermeiro = await profissional_factory(cargo=CargoProfissional.ENFERMEIRO)
    paciente = await paciente_factory()

    token_medico = token_factory(medico)
    token_enfermeiro = token_factory(enfermeiro)

    criar = await client.post(
        "/api/v1/triagens/",
        json={
            "paciente_id": str(paciente.id),
            "sinais_vitais": sinais_vitais_azul,
            "sintomas": [],
            "queixa_principal": "Rotina",
        },
        headers={"Authorization": f"Bearer {token_medico}"},
    )

    confirmar = await client.post(
        f"/api/v1/triagens/{criar.json()['id']}/confirmar",
        json={"nivel_confirmado": "vermelho"},
        headers={"Authorization": f"Bearer {token_enfermeiro}"},
    )

    assert confirmar.status_code == 403
