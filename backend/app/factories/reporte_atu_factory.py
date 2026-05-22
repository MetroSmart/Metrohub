"""
Patrón Abstract Factory — familias de reporte oficial ATU (RF06).

Garantiza que encabezado, KPIs y tablas del mismo reporte usen el mismo formato.
"""
from abc import ABC, abstractmethod
from typing import Any

from app.export.base import SeccionReporte
from app.export.factory import ExportadorReporteFactory


class SeccionEncabezado(SeccionReporte):
    def renderizar(self, datos: dict[str, Any]) -> str:
        return (
            f"METROHUB — Reporte ATU\n"
            f"Sistema: {datos.get('sistema', 'MetroSmart')}\n"
            f"Fecha: {datos.get('fecha')}\n"
            "---\n"
        )


class SeccionKpis(SeccionReporte):
    def renderizar(self, datos: dict[str, Any]) -> str:
        kpis = datos.get("kpis", {})
        lineas = ["KPIs operativos:"]
        for clave, valor in kpis.items():
            lineas.append(f"  - {clave}: {valor}")
        return "\n".join(lineas) + "\n"


class SeccionTablaResumen(SeccionReporte):
    def renderizar(self, datos: dict[str, Any]) -> str:
        extras = datos.get("extras", {})
        lineas = ["Resumen adicional:"]
        for clave, valor in extras.items():
            lineas.append(f"  - {clave}: {valor}")
        return "\n".join(lineas) + "\n"


class FabricaSeccionesReporte(ABC):
    @abstractmethod
    def crear_encabezado(self) -> SeccionReporte:
        pass

    @abstractmethod
    def crear_kpis(self) -> SeccionReporte:
        pass

    @abstractmethod
    def crear_tabla(self) -> SeccionReporte:
        pass


class FabricaReporteATUPdf(FabricaSeccionesReporte):
    def crear_encabezado(self) -> SeccionReporte:
        return SeccionEncabezado()

    def crear_kpis(self) -> SeccionReporte:
        return SeccionKpis()

    def crear_tabla(self) -> SeccionReporte:
        return SeccionTablaResumen()


class FabricaReporteATUXlsx(FabricaSeccionesReporte):
    """Misma familia de secciones; el formato final lo define el exportador."""

    def crear_encabezado(self) -> SeccionReporte:
        return SeccionEncabezado()

    def crear_kpis(self) -> SeccionReporte:
        return SeccionKpis()

    def crear_tabla(self) -> SeccionReporte:
        return SeccionTablaResumen()


_FABRICAS_SECCIONES: dict[str, type[FabricaSeccionesReporte]] = {
    "pdf": FabricaReporteATUPdf,
    "xlsx": FabricaReporteATUXlsx,
}


class ReporteATUFactory:
    """Abstract Factory: ensambla familia de secciones + exportador coherente."""

    @staticmethod
    def obtener_fabrica_secciones(formato: str) -> FabricaSeccionesReporte:
        clase = _FABRICAS_SECCIONES.get(formato.lower())
        if not clase:
            raise ValueError(f"Familia de reporte '{formato}' no soportada")
        return clase()

    @classmethod
    def generar_reporte_completo(
        cls, formato: str, datos: dict[str, Any]
    ) -> tuple[bytes, str, str]:
        fabrica = cls.obtener_fabrica_secciones(formato)
        encabezado = fabrica.crear_encabezado().renderizar(datos)
        kpis = fabrica.crear_kpis().renderizar(datos)
        tabla = fabrica.crear_tabla().renderizar(datos)
        payload = {
            "contenido_texto": encabezado + kpis + tabla,
            "kpis": datos.get("kpis", {}),
            "fecha": datos.get("fecha"),
            "formato_familia": formato,
        }
        exportador = ExportadorReporteFactory.crear(formato)
        return exportador.exportar(payload)
