"""Servicio RF06 — exportación con Factory Method y Abstract Factory ATU."""
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.export.factory import ExportadorReporteFactory
from app.factories.reporte_atu_factory import ReporteATUFactory
from app.services import dashboard_service


def exportar_dashboard(
    db: Session,
    formato: str,
    usar_familia_atu: bool = True,
    extras: dict[str, Any] | None = None,
) -> tuple[bytes, str, str]:
    kpis = dashboard_service.obtener_kpis(db)
    datos = {
        "sistema": "MetroHub",
        "fecha": str(kpis.get("fecha", date.today())),
        "kpis": {k: v for k, v in kpis.items() if k != "fecha"},
        "extras": extras or {},
    }
    if usar_familia_atu:
        return ReporteATUFactory.generar_reporte_completo(formato, datos)
    exportador = ExportadorReporteFactory.crear(formato)
    return exportador.exportar(datos)
