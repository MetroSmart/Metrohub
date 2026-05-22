"""Contrato del patrón Prototype — copia de entidades de programación."""
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Prototype(ABC, Generic[T]):
    @abstractmethod
    def clone(self, **ajustes: Any) -> T:
        """Crea una copia del objeto aplicando ajustes (p. ej. nueva fecha)."""

    def _copiar_estado(self, estado: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(estado)
