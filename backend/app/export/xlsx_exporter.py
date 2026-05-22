import csv
import io
from typing import Any

from app.export.base import ExportadorReporte


class XlsxExporter(ExportadorReporte):
    """Exportador tabular CSV-compatible (stub XLSX hasta openpyxl en Sprint 2)."""

    def exportar(self, datos: dict[str, Any]) -> tuple[bytes, str, str]:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["clave", "valor"])
        for clave, valor in datos.items():
            writer.writerow([clave, valor])
        contenido = buffer.getvalue().encode("utf-8-sig")
        return (
            contenido,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        )
