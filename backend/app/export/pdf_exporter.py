import json
from typing import Any

from app.export.base import ExportadorReporte


class PdfExporter(ExportadorReporte):
    """Exportador PDF (stub textual hasta integrar librería en Sprint 2)."""

    def exportar(self, datos: dict[str, Any]) -> tuple[bytes, str, str]:
        cuerpo = (
            "%PDF-1.4 stub MetroHub\n"
            "%% Reporte ATU\n"
            f"{json.dumps(datos, ensure_ascii=False, indent=2, default=str)}"
        )
        return cuerpo.encode("utf-8"), "application/pdf", "pdf"
