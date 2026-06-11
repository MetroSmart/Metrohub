"""SCRUM-QA-21: pruebas unitarias del patrón Abstract Factory de reportes ATU (RF06)."""
import pytest

from app.export.base import SeccionReporte
from app.factories.reporte_atu_factory import (
    FabricaReporteATUPdf,
    FabricaReporteATUXlsx,
    FabricaSeccionesReporte,
    ReporteATUFactory,
    SeccionEncabezado,
    SeccionKpis,
    SeccionTablaResumen,
)


def _datos():
    return {
        "sistema": "MetroHub",
        "fecha": "2026-06-11",
        "kpis": {"rutas_activas": 3, "conflictos_abiertos": 1},
        "extras": {"observaciones": "sin novedades"},
    }


# ── Selección de fábrica ──────────────────────────────────
def test_obtener_fabrica_pdf():
    fabrica = ReporteATUFactory.obtener_fabrica_secciones("pdf")
    assert isinstance(fabrica, FabricaReporteATUPdf)
    assert isinstance(fabrica, FabricaSeccionesReporte)


def test_obtener_fabrica_xlsx():
    fabrica = ReporteATUFactory.obtener_fabrica_secciones("xlsx")
    assert isinstance(fabrica, FabricaReporteATUXlsx)


def test_obtener_fabrica_case_insensitive():
    assert isinstance(ReporteATUFactory.obtener_fabrica_secciones("PDF"), FabricaReporteATUPdf)


def test_obtener_fabrica_invalida_value_error():
    with pytest.raises(ValueError, match="no soportada"):
        ReporteATUFactory.obtener_fabrica_secciones("csv")


# ── Coherencia de la familia ──────────────────────────────
@pytest.mark.parametrize("formato", ["pdf", "xlsx"])
def test_fabrica_crea_familia_coherente(formato):
    fabrica = ReporteATUFactory.obtener_fabrica_secciones(formato)
    encabezado = fabrica.crear_encabezado()
    kpis = fabrica.crear_kpis()
    tabla = fabrica.crear_tabla()
    assert isinstance(encabezado, SeccionEncabezado)
    assert isinstance(kpis, SeccionKpis)
    assert isinstance(tabla, SeccionTablaResumen)
    for seccion in (encabezado, kpis, tabla):
        assert isinstance(seccion, SeccionReporte)


# ── Renderizado de secciones ──────────────────────────────
def test_seccion_encabezado_renderiza_sistema_y_fecha():
    texto = SeccionEncabezado().renderizar(_datos())
    assert "METROHUB — Reporte ATU" in texto
    assert "Sistema: MetroHub" in texto
    assert "Fecha: 2026-06-11" in texto


def test_seccion_kpis_lista_valores():
    texto = SeccionKpis().renderizar(_datos())
    assert "KPIs operativos:" in texto
    assert "rutas_activas: 3" in texto
    assert "conflictos_abiertos: 1" in texto


def test_seccion_tabla_renderiza_extras():
    texto = SeccionTablaResumen().renderizar(_datos())
    assert "Resumen adicional:" in texto
    assert "observaciones: sin novedades" in texto


def test_secciones_toleran_datos_vacios():
    for seccion in (SeccionEncabezado(), SeccionKpis(), SeccionTablaResumen()):
        assert isinstance(seccion.renderizar({}), str)


# ── Reporte completo ──────────────────────────────────────
def test_generar_reporte_completo_pdf():
    contenido, media_type, ext = ReporteATUFactory.generar_reporte_completo("pdf", _datos())
    assert contenido[:4] == b"%PDF"
    assert media_type == "application/pdf"
    assert ext == "pdf"


def test_generar_reporte_completo_xlsx():
    contenido, media_type, ext = ReporteATUFactory.generar_reporte_completo("xlsx", _datos())
    assert contenido[:2] == b"PK"
    assert media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert ext == "xlsx"


def test_generar_reporte_formato_invalido_value_error():
    with pytest.raises(ValueError, match="no soportada"):
        ReporteATUFactory.generar_reporte_completo("csv", _datos())
