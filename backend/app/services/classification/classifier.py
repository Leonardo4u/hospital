"""Facade for clinical classification."""

from __future__ import annotations

from backend.app.services.classification.strategies import ClassificationStrategy
from backend.app.services.classification.types import EntradaClassificacao, ResultadoClassificacao


class Classifier:
    """Delegates classification to an injected strategy."""

    def __init__(self, strategy: ClassificationStrategy) -> None:
        """Store the injected classification strategy."""
        self._strategy = strategy

    def classificar(self, entrada: EntradaClassificacao) -> ResultadoClassificacao:
        """Validate the input and delegate classification."""
        if entrada is None:
            raise ValueError("entrada nao pode ser None.")
        return self._strategy.classificar(entrada)
