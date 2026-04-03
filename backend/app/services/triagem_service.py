"""Service that orchestrates triage classification workflows."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.logging_config import get_logger
from backend.app.models.profissional import CargoProfissional
from backend.app.models.triagem import OrigemClassificacao, Triagem
from backend.app.repositories.audit_repository import AuditRepository
from backend.app.repositories.paciente_repository import PacienteRepository
from backend.app.repositories.triagem_repository import TriagemRepository
from backend.app.schemas.triagem import ConfirmacaoIn, TriagemCreate, TriagemCreatedOut, TriagemOut
from backend.app.services.classification import (
    Classifier,
    EntradaClassificacao,
    ResultadoClassificacao,
    RiscoNivel,
    SinaisVitais,
    Sintoma,
)

logger = get_logger(__name__)


class TriagemService:
    """Service that coordinates classification, persistence, and auditing."""

    def __init__(
        self,
        triagem_repo: TriagemRepository,
        paciente_repo: PacienteRepository,
        audit_repo: AuditRepository,
        classifier: Classifier,
        db: AsyncSession,
    ) -> None:
        """Store injected triage dependencies."""
        self._triagem_repo = triagem_repo
        self._paciente_repo = paciente_repo
        self._audit_repo = audit_repo
        self._classifier = classifier
        self._db = db

    async def classificar(
        self,
        dados: TriagemCreate,
        profissional_id: uuid.UUID,
        ip: str,
    ) -> TriagemCreatedOut:
        """Classify and persist a triage record."""
        paciente = await self._paciente_repo.buscar_por_id(self._db, dados.paciente_id)
        if paciente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente nao encontrado.",
            )

        try:
            sinais_vitais = SinaisVitais(**dados.sinais_vitais.model_dump())
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        sintomas = [Sintoma(**sintoma.model_dump()) for sintoma in dados.sintomas]
        entrada = EntradaClassificacao(
            sinais_vitais=sinais_vitais,
            sintomas=sintomas,
            idade_anos=self._calcular_idade(paciente.data_nascimento),
            queixa_principal=dados.queixa_principal,
        )
        resultado = self._classifier.classificar(entrada)

        triagem = Triagem(
            paciente_id=dados.paciente_id,
            profissional_id=profissional_id,
            sinais_vitais=dados.sinais_vitais.model_dump(),
            sintomas=[sintoma.model_dump() for sintoma in dados.sintomas],
            queixa_principal=dados.queixa_principal,
            nivel_calculado=resultado.nivel,
            nivel_confirmado=None,
            justificativa=resultado.justificativa,
            discriminadores_ativados=resultado.discriminadores_ativados,
            confianca=resultado.confianca,
            origem=OrigemClassificacao(resultado.origem),
            confirmado_em=None,
            usado_em_treino=False,
        )
        triagem_persistida = await self._triagem_repo.criar(self._db, triagem)
        await self._audit_repo.registrar(
            db=self._db,
            entidade="triagem",
            entidade_id=triagem_persistida.id,
            acao="classificar",
            profissional_id=profissional_id,
            payload_antes=None,
            payload_depois=self._serializar_resultado(resultado),
            ip=ip,
        )
        logger.info(
            "triagem_classificada",
            extra={
                "triagem_id": str(triagem_persistida.id),
                "nivel_resultado": resultado.nivel.value,
                "origem": resultado.origem,
                "confianca": resultado.confianca,
            },
        )

        return TriagemCreatedOut(id=triagem_persistida.id, criado_em=triagem_persistida.criado_em)

    async def buscar(self, triagem_id: uuid.UUID, profissional_id: uuid.UUID) -> TriagemOut:
        """Fetch a triage result by id."""
        del profissional_id
        triagem = await self._triagem_repo.buscar_por_id(self._db, triagem_id)
        if triagem is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triagem nao encontrada.",
            )

        return TriagemOut.model_validate(self._serializar_triagem(triagem))

    async def confirmar(
        self,
        triagem_id: uuid.UUID,
        dados: ConfirmacaoIn,
        profissional_id: uuid.UUID,
        cargo_profissional: CargoProfissional,
        ip: str,
    ) -> TriagemOut:
        """Confirm a calculated triage level."""
        self._validar_permissao_confirmacao(cargo_profissional, dados.nivel_confirmado)

        triagem = await self._triagem_repo.buscar_por_id(self._db, triagem_id)
        if triagem is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triagem nao encontrada.",
            )
        if triagem.nivel_confirmado is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Triagem ja confirmada",
            )

        atualizada = await self._triagem_repo.confirmar(self._db, triagem_id, dados.nivel_confirmado)
        if atualizada is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triagem nao encontrada.",
            )

        await self._audit_repo.registrar(
            db=self._db,
            entidade="triagem",
            entidade_id=atualizada.id,
            acao="confirmar",
            profissional_id=profissional_id,
            payload_antes={"nivel": triagem.nivel_calculado.value},
            payload_depois={"nivel": dados.nivel_confirmado.value},
            ip=ip,
        )
        if dados.nivel_confirmado != triagem.nivel_calculado:
            await self._audit_repo.registrar(
                db=self._db,
                entidade="triagem",
                entidade_id=atualizada.id,
                acao="corrigir",
                profissional_id=profissional_id,
                payload_antes={"nivel": triagem.nivel_calculado.value},
                payload_depois={"nivel": dados.nivel_confirmado.value},
                ip=ip,
            )
        logger.info(
            "triagem_confirmada",
            extra={
                "triagem_id": str(atualizada.id),
                "nivel_resultado": dados.nivel_confirmado.value,
                "origem": atualizada.origem.value,
                "confianca": atualizada.confianca,
            },
        )

        return TriagemOut.model_validate(self._serializar_triagem(atualizada))

    async def listar_por_paciente(self, paciente_id: uuid.UUID) -> list[TriagemOut]:
        """List triages for a patient."""
        triagens = await self._triagem_repo.listar_por_paciente(self._db, paciente_id)
        return [TriagemOut.model_validate(self._serializar_triagem(triagem)) for triagem in triagens]

    @staticmethod
    def _serializar_resultado(resultado: ResultadoClassificacao) -> dict[str, object]:
        payload = asdict(resultado)
        payload["nivel"] = resultado.nivel.value
        return payload

    @staticmethod
    def _serializar_triagem(triagem: Triagem) -> dict[str, object]:
        return {
            "id": triagem.id,
            "paciente_id": triagem.paciente_id,
            "profissional_id": triagem.profissional_id,
            "sinais_vitais": triagem.sinais_vitais,
            "sintomas": triagem.sintomas,
            "queixa_principal": triagem.queixa_principal,
            "nivel_calculado": triagem.nivel_calculado.value,
            "nivel_confirmado": triagem.nivel_confirmado.value if triagem.nivel_confirmado else None,
            "justificativa": triagem.justificativa,
            "discriminadores_ativados": triagem.discriminadores_ativados,
            "confianca": triagem.confianca,
            "origem": triagem.origem.value,
            "confirmado_em": triagem.confirmado_em,
            "usado_em_treino": triagem.usado_em_treino,
            "criado_em": triagem.criado_em,
            "atualizado_em": triagem.atualizado_em,
        }

    @staticmethod
    def _calcular_idade(data_nascimento: date) -> int:
        hoje = date.today()
        return hoje.year - data_nascimento.year - (
            (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
        )

    @staticmethod
    def _validar_permissao_confirmacao(
        cargo_profissional: CargoProfissional,
        nivel_confirmado: RiscoNivel,
    ) -> None:
        if cargo_profissional == CargoProfissional.TECNICO:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tecnico nao possui permissao para confirmar classificacao.",
            )

        if (
            cargo_profissional == CargoProfissional.ENFERMEIRO
            and nivel_confirmado in {RiscoNivel.LARANJA, RiscoNivel.VERMELHO}
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Enfermeiro nao pode confirmar classificacao laranja ou vermelha.",
            )
