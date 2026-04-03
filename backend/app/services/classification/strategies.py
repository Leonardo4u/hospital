"""Classification strategies."""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from backend.app.services.classification.rules.manchester_engine import ManchesterEngine
from backend.app.services.classification.types import EntradaClassificacao, ResultadoClassificacao


class ClassificationStrategy(Protocol):
    """Contract for classification strategies."""

    def classificar(self, entrada: EntradaClassificacao) -> ResultadoClassificacao:
        """Classify a clinical case."""


class ManchesterStrategy:
    """Strategy backed by the Manchester engine."""

    def __init__(self, engine: ManchesterEngine | None = None) -> None:
        """Initialize the Manchester-backed strategy."""
        self._engine = engine or ManchesterEngine()

    def classificar(self, entrada: EntradaClassificacao) -> ResultadoClassificacao:
        """Classify a case with Manchester rules."""
        return self._engine.classificar(entrada)


class MLStrategy:
    """Placeholder strategy for future ML support."""

    def classificar(self, entrada: EntradaClassificacao) -> ResultadoClassificacao:
        """Signal that ML classification is not ready."""
        raise NotImplementedError(
            "MLStrategy requer minimo de 500 amostras confirmadas. Use ManchesterStrategy."
        )


class HybridStrategy:
    """Strategy that combines Manchester and ML when possible."""

    def __init__(
        self,
        manchester_strategy: ClassificationStrategy,
        ml_strategy: ClassificationStrategy,
    ) -> None:
        """Initialize hybrid dependencies via injection."""
        self._manchester_strategy = manchester_strategy
        self._ml_strategy = ml_strategy

    def classificar(self, entrada: EntradaClassificacao) -> ResultadoClassificacao:
        """Classify with Manchester first and reconcile with ML."""
        resultado_manchester = self._manchester_strategy.classificar(entrada)
        try:
            resultado_ml = self._ml_strategy.classificar(entrada)
        except NotImplementedError:
            return resultado_manchester

        if resultado_ml.nivel == resultado_manchester.nivel:
            return replace(resultado_manchester, origem="hibrido")
        return resultado_manchester
