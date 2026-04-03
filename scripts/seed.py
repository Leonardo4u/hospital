"""Seed initial data for local and homologation environments."""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.core.config import settings
from backend.app.core.security import hash_senha
from backend.app.models.paciente import Paciente, SexoPaciente
from backend.app.models.profissional import CargoProfissional, Profissional
from backend.app.models.triagem import OrigemClassificacao, Triagem
from backend.app.services.classification import RiscoNivel


PROFISSIONAIS = [
    {
        "nome": "Administrador Clinico",
        "email": "admin@triagem.local",
        "senha": "Admin@2024",
        "crm": "123456",
        "cargo": CargoProfissional.MEDICO,
    },
    {
        "nome": "Enf. Juliana Costa",
        "email": "juliana@triagem.local",
        "senha": "Enfermeiro@2024",
        "crm": None,
        "cargo": CargoProfissional.ENFERMEIRO,
    },
    {
        "nome": "Enf. Rafael Nunes",
        "email": "rafael@triagem.local",
        "senha": "Enfermeiro@2024",
        "crm": None,
        "cargo": CargoProfissional.ENFERMEIRO,
    },
    {
        "nome": "Tec. Camila Souza",
        "email": "camila@triagem.local",
        "senha": "Tecnico@2024",
        "crm": None,
        "cargo": CargoProfissional.TECNICO,
    },
]

PACIENTES = [
    ("Mariana Alves", date(1988, 4, 12), "11144477735", SexoPaciente.F, "Mae - 11999990001"),
    ("Carlos Menezes", date(1975, 9, 30), "52998224725", SexoPaciente.M, "Esposa - 11999990002"),
    ("Fernanda Rocha", date(1996, 1, 5), "16899535009", SexoPaciente.F, "Pai - 11999990003"),
    ("Lucas Martins", date(2003, 7, 19), "39053344705", SexoPaciente.M, "Irma - 11999990004"),
    ("Aline Batista", date(1969, 11, 23), "11122233396", SexoPaciente.F, "Filho - 11999990005"),
]

TRIAGENS_EXEMPLO = [
    (RiscoNivel.VERMELHO, {"frequencia_cardiaca": 165, "pressao_sistolica": 78, "pressao_diastolica": 50, "saturacao_o2": 82.0, "temperatura": 37.2, "frequencia_respiratoria": 30, "glasgow": 7}, [{"codigo": "dispneia", "descricao": "Dispneia intensa", "peso": 0.95}], "Dispneia intensa com rebaixamento", RiscoNivel.VERMELHO),
    (RiscoNivel.VERMELHO, {"frequencia_cardiaca": 152, "pressao_sistolica": 85, "pressao_diastolica": 55, "saturacao_o2": 84.0, "temperatura": 36.4, "frequencia_respiratoria": 28, "glasgow": 6}, [{"codigo": "alteracao_consciencia", "descricao": "Alteracao de consciencia", "peso": 0.98}], "Rebaixamento do nivel de consciencia", RiscoNivel.VERMELHO),
    (RiscoNivel.LARANJA, {"frequencia_cardiaca": 112, "pressao_sistolica": 132, "pressao_diastolica": 82, "saturacao_o2": 96.0, "temperatura": 37.0, "frequencia_respiratoria": 22, "glasgow": 15}, [{"codigo": "dor_toracica", "descricao": "Dor toracica", "peso": 0.9}], "Dor toracica com taquicardia", RiscoNivel.LARANJA),
    (RiscoNivel.LARANJA, {"frequencia_cardiaca": 98, "pressao_sistolica": 140, "pressao_diastolica": 88, "saturacao_o2": 94.0, "temperatura": 37.6, "frequencia_respiratoria": 20, "glasgow": 10}, [{"codigo": "alteracao_consciencia", "descricao": "Confusao mental", "peso": 0.86}], "Confusao mental aguda", RiscoNivel.LARANJA),
    (RiscoNivel.AMARELO, {"frequencia_cardiaca": 102, "pressao_sistolica": 178, "pressao_diastolica": 100, "saturacao_o2": 92.0, "temperatura": 39.8, "frequencia_respiratoria": 22, "glasgow": 15}, [{"codigo": "febre", "descricao": "Febre alta", "peso": 0.72}], "Febre persistente e mal-estar", RiscoNivel.AMARELO),
    (RiscoNivel.AMARELO, {"frequencia_cardiaca": 96, "pressao_sistolica": 182, "pressao_diastolica": 105, "saturacao_o2": 93.0, "temperatura": 37.1, "frequencia_respiratoria": 18, "glasgow": 15}, [{"codigo": "cefaleia_intensa", "descricao": "Cefaleia intensa", "peso": 0.7}], "Cefaleia intensa associada a hipertensao", RiscoNivel.AMARELO),
    (RiscoNivel.VERDE, {"frequencia_cardiaca": 88, "pressao_sistolica": 122, "pressao_diastolica": 80, "saturacao_o2": 98.0, "temperatura": 37.0, "frequencia_respiratoria": 16, "glasgow": 15}, [{"codigo": "dor_garganta", "descricao": "Dor de garganta", "peso": 0.25}], "Odinofagia ha dois dias", RiscoNivel.VERDE),
    (RiscoNivel.VERDE, {"frequencia_cardiaca": 74, "pressao_sistolica": 118, "pressao_diastolica": 78, "saturacao_o2": 99.0, "temperatura": 36.8, "frequencia_respiratoria": 15, "glasgow": 15}, [{"codigo": "dor_lombar", "descricao": "Dor lombar", "peso": 0.3}], "Dor lombar sem sinais de alarme", RiscoNivel.VERDE),
    (RiscoNivel.AZUL, {"frequencia_cardiaca": 70, "pressao_sistolica": 116, "pressao_diastolica": 76, "saturacao_o2": 99.0, "temperatura": 36.6, "frequencia_respiratoria": 14, "glasgow": 15}, [], "Reavaliacao sem queixa aguda", RiscoNivel.AZUL),
    (RiscoNivel.AZUL, {"frequencia_cardiaca": 72, "pressao_sistolica": 120, "pressao_diastolica": 80, "saturacao_o2": 98.0, "temperatura": 36.7, "frequencia_respiratoria": 14, "glasgow": 15}, [], "Orientacao administrativa sem sintomas", RiscoNivel.AZUL),
]


async def validar_migracoes(session: AsyncSession) -> None:
    """Fail fast if migrations are missing."""
    def _validar(sync_session) -> None:
        inspector = inspect(sync_session.bind)
        tabelas = set(inspector.get_table_names())
        if "alembic_version" not in tabelas:
            raise RuntimeError("Tabela alembic_version ausente. Execute as migrations antes do seed.")
        obrigatorias = {"profissionais", "pacientes", "triagens", "audit_logs"}
        if not obrigatorias.issubset(tabelas):
            raise RuntimeError("Migrations nao aplicadas integralmente. Tabelas essenciais ausentes.")

    await session.run_sync(_validar)


async def main() -> None:
    """Execute the seed routine."""
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    criados_profissionais = 0
    criados_pacientes = 0
    criadas_triagens = 0

    try:
        async with session_factory() as session:
            await validar_migracoes(session)

            admin_existente = await session.scalar(
                select(Profissional).where(Profissional.email == "admin@triagem.local")
            )
            if admin_existente is not None:
                print("Seed ja aplicado anteriormente. Nenhuma duplicacao realizada.")
                return

            profissionais: list[Profissional] = []
            for item in PROFISSIONAIS:
                profissional = Profissional(
                    nome=item["nome"],
                    email=item["email"],
                    senha_hash=hash_senha(item["senha"]),
                    crm=item["crm"],
                    cargo=item["cargo"],
                )
                session.add(profissional)
                profissionais.append(profissional)
                criados_profissionais += 1

            pacientes: list[Paciente] = []
            for nome, nascimento, cpf, sexo, contato in PACIENTES:
                paciente = Paciente(
                    nome_completo=nome,
                    data_nascimento=nascimento,
                    cpf=cpf,
                    sexo=sexo,
                    contato_emergencia=contato,
                )
                session.add(paciente)
                pacientes.append(paciente)
                criados_pacientes += 1

            await session.flush()

            for indice, exemplo in enumerate(TRIAGENS_EXEMPLO):
                nivel_calculado, sinais_vitais, sintomas, queixa, nivel_confirmado = exemplo
                paciente = pacientes[indice % len(pacientes)]
                profissional = profissionais[indice % len(profissionais)]
                triagem = Triagem(
                    paciente_id=paciente.id,
                    profissional_id=profissional.id,
                    sinais_vitais=sinais_vitais,
                    sintomas=sintomas,
                    queixa_principal=queixa,
                    nivel_calculado=nivel_calculado,
                    nivel_confirmado=nivel_confirmado,
                    justificativa=f"Triagem de exemplo para nivel {nivel_calculado.value}.",
                    discriminadores_ativados=[f"seed_{nivel_calculado.value.lower()}"],
                    confianca=1.0,
                    origem=OrigemClassificacao.REGRAS,
                    confirmado_em=datetime.now(UTC),
                    usado_em_treino=False,
                )
                session.add(triagem)
                criadas_triagens += 1

            await session.commit()
    except Exception as exc:
        raise SystemExit(f"Falha ao executar seed: {exc}") from exc
    finally:
        await engine.dispose()

    print(f"Criados: {criados_profissionais} profissionais, {criados_pacientes} pacientes, {criadas_triagens} triagens")


if __name__ == "__main__":
    asyncio.run(main())
