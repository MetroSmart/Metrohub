"""
Patrón Factory Method — RF06 (exportación PDF / XLSX).
"""
from app.export.base import ExportadorReporte
from app.export.pdf_exporter import PdfExporter
from app.export.xlsx_exporter import XlsxExporter

_EXPORTADORES: dict[str, type[ExportadorReporte]] = {
    "pdf": PdfExporter,
    "xlsx": XlsxExporter,
}


class ExportadorReporteFactory:
    @staticmethod
    def crear(formato: str) -> ExportadorReporte:
        clase = _EXPORTADORES.get(formato.lower())
        if not clase:
            disponibles = ", ".join(sorted(_EXPORTADORES))
            raise ValueError(f"Formato '{formato}' no soportado. Disponibles: {disponibles}")
        return clase()
