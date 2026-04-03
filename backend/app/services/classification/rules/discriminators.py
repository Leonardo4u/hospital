"""Pure Manchester discriminators."""

from __future__ import annotations

from backend.app.services.classification.types import EntradaClassificacao, RiscoNivel


def avaliar_comprometimento_via_aerea(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate critical airway compromise."""
    sinais = entrada.sinais_vitais
    if sinais.glasgow < 8 or sinais.saturacao_o2 < 85:
        return RiscoNivel.VERMELHO
    return None


def avaliar_choque(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate shock criteria."""
    sinais = entrada.sinais_vitais
    if sinais.pressao_sistolica < 80 or (
        sinais.frequencia_cardiaca > 150 and sinais.pressao_sistolica < 90
    ):
        return RiscoNivel.VERMELHO
    return None


def avaliar_dor_toracica(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate chest pain with tachycardia."""
    sintomas_codificados = {sintoma.codigo for sintoma in entrada.sintomas}
    if "dor_toracica" in sintomas_codificados and entrada.sinais_vitais.frequencia_cardiaca > 100:
        return RiscoNivel.LARANJA
    return None


def avaliar_alteracao_nivel_consciencia(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate moderate consciousness alteration."""
    glasgow = entrada.sinais_vitais.glasgow
    if 8 <= glasgow <= 13:
        return RiscoNivel.LARANJA
    return None


def avaliar_febre_alta(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate high fever."""
    if entrada.sinais_vitais.temperatura >= 39.5:
        return RiscoNivel.AMARELO
    return None


def avaliar_hipertensao_grave(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate severe hypertension."""
    if entrada.sinais_vitais.pressao_sistolica >= 180:
        return RiscoNivel.AMARELO
    return None


def avaliar_saturacao_limiar(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate borderline oxygen saturation."""
    saturacao_o2 = entrada.sinais_vitais.saturacao_o2
    if 85 <= saturacao_o2 <= 93:
        return RiscoNivel.AMARELO
    return None


def avaliar_sintomas_leves(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate low-acuity symptoms."""
    if entrada.sintomas:
        return RiscoNivel.VERDE
    return None


def avaliar_sem_queixa_aguda(entrada: EntradaClassificacao) -> RiscoNivel | None:
    """Evaluate absence of acute complaint."""
    if not entrada.sintomas and entrada.sinais_vitais.glasgow == 15:
        return RiscoNivel.AZUL
    return None
