"""Public exports for the classification package."""

from backend.app.services.classification.classifier import Classifier
from backend.app.services.classification.strategies import ClassificationStrategy, ManchesterStrategy
from backend.app.services.classification.types import (
    EntradaClassificacao,
    ResultadoClassificacao,
    RiscoNivel,
    SinaisVitais,
    Sintoma,
)

__all__ = [
    "Classifier",
    "ClassificationStrategy",
    "EntradaClassificacao",
    "ResultadoClassificacao",
    "RiscoNivel",
    "SinaisVitais",
    "Sintoma",
    "ManchesterStrategy",
]
