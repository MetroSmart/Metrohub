"""Contratos de exportación — RF06."""
from abc import ABC, abstractmethod
from typing import Any


class ExportadorReporte(ABC):
    @abstractmethod
    def exportar(self, datos: dict[str, Any]) -> tuple[bytes, str, str]:
        """
        Retorna (contenido, media_type, extension_sin_punto).
        """


class SeccionReporte(ABC):
    """Componente de un reporte (usado por Abstract Factory ATU)."""

    @abstractmethod
    def renderizar(self, datos: dict[str, Any]) -> str:
        pass
