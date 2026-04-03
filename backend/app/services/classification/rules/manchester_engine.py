"""Manchester rules orchestration."""

from __future__ import annotations

from collections.abc import Callable

from backend.app.services.classification.rules.discriminators import (
    avaliar_alteracao_nivel_consciencia,
    avaliar_choque,
    avaliar_comprometimento_via_aerea,
    avaliar_dor_toracica,
    avaliar_febre_alta,
    avaliar_hipertensao_grave,
    avaliar_saturacao_limiar,
    avaliar_sem_queixa_aguda,
    avaliar_sintomas_leves,
)
from backend.app.services.classification.types import (
    EntradaClassificacao,
    ResultadoClassificacao,
    RiscoNivel,
)

_DISCRIMINADORES: tuple[
    tuple[str, Callable[[EntradaClassificacao], RiscoNivel | None]],
    ...,
] = (
    ("avaliar_comprometimento_via_aerea", avaliar_comprometimento_via_aerea),
    ("avaliar_choque", avaliar_choque),
    ("avaliar_dor_toracica", avaliar_dor_toracica),
    ("avaliar_alteracao_nivel_consciencia", avaliar_alteracao_nivel_consciencia),
    ("avaliar_febre_alta", avaliar_febre_alta),
    ("avaliar_hipertensao_grave", avaliar_hipertensao_grave),
    ("avaliar_saturacao_limiar", avaliar_saturacao_limiar),
    ("avaliar_sintomas_leves", avaliar_sintomas_leves),
    ("avaliar_sem_queixa_aguda", avaliar_sem_queixa_aguda),
)

_PRIORIDADE_NIVEL: dict[RiscoNivel, int] = {
    RiscoNivel.VERMELHO: 0,
    RiscoNivel.LARANJA: 1,
    RiscoNivel.AMARELO: 2,
    RiscoNivel.VERDE: 3,
    RiscoNivel.AZUL: 4,
}


class ManchesterEngine:
    """Orchestrates Manchester discriminators."""

    def classificar(self, entrada: EntradaClassificacao) -> ResultadoClassificacao:
        """Classify a case using rules."""
        ativados: list[tuple[str, RiscoNivel]] = []
        for nome, discriminador in _DISCRIMINADORES:
            nivel = discriminador(entrada)
            if nivel is not None:
                ativados.append((nome, nivel))

        if ativados:
            nivel_final = min(ativados, key=lambda item: _PRIORIDADE_NIVEL[item[1]])[1]
            nomes_ativados = [nome for nome, _ in ativados]
            justificativa = (
                "Discriminadores ativados: " + ", ".join(nomes_ativados) + "."
            )
        else:
            nivel_final = RiscoNivel.AZUL
            nomes_ativados = []
            justificativa = "Nenhum discriminador ativado."

        return ResultadoClassificacao(
            nivel=nivel_final,
            justificativa=justificativa,
            discriminadores_ativados=nomes_ativados,
            confianca=1.0,
            origem="regras",
        )
