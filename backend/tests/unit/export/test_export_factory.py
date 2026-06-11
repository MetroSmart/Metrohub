"""SCRUM-QA-20: pruebas unitarias del patrón Factory Method de exportación (RF06)."""
import pytest

from app.export.base import ExportadorReporte
from app.export.factory import ExportadorReporteFactory
from app.export.pdf_exporter import PdfExporter
from app.export.xlsx_exporter import XlsxExporter

MIME_PDF = "application/pdf"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _datos_minimos():
    return {
        "sistema": "MetroHub",
        "fecha": "2026-06-11",
        "kpis": {
            "rutas_activas": 3,
            "choferes_activos": 12,
            "buses_operativos": 8,
            "conflictos_abiertos": 1,
        },
        "rutas": [],
        "buses": [],
        "choferes": [],
        "alertas_doc": [],
        "programaciones": [],
        "conflictos": [],
        "extras": {},
    }


# ── Factory Method ────────────────────────────────────────
def test_crear_pdf_devuelve_pdf_exporter():
    exportador = ExportadorReporteFactory.crear("pdf")
    assert isinstance(exportador, PdfExporter)
    assert isinstance(exportador, ExportadorReporte)


def test_crear_xlsx_devuelve_xlsx_exporter():
    exportador = ExportadorReporteFactory.crear("xlsx")
    assert isinstance(exportador, XlsxExporter)
    assert isinstance(exportador, ExportadorReporte)


@pytest.mark.parametrize("formato,clase", [
    ("PDF", PdfExporter),
    ("Pdf", PdfExporter),
    ("XLSX", XlsxExporter),
    ("Xlsx", XlsxExporter),
])
def test_crear_es_case_insensitive(formato, clase):
    assert isinstance(ExportadorReporteFactory.crear(formato), clase)


@pytest.mark.parametrize("formato", ["csv", "docx", "", "pdfx"])
def test_crear_formato_invalido_value_error(formato):
    with pytest.raises(ValueError, match="no soportado"):
        ExportadorReporteFactory.crear(formato)


def test_crear_devuelve_instancias_nuevas():
    a = ExportadorReporteFactory.crear("pdf")
    b = ExportadorReporteFactory.crear("pdf")
    assert a is not b


# ── Productos concretos ───────────────────────────────────
def test_pdf_exportar_bytes_y_mime():
    contenido, media_type, ext = PdfExporter().exportar(_datos_minimos())
    assert isinstance(contenido, bytes)
    assert len(contenido) > 0
    assert contenido[:4] == b"%PDF"
    assert media_type == MIME_PDF
    assert ext == "pdf"


def test_xlsx_exportar_bytes_y_mime():
    contenido, media_type, ext = XlsxExporter().exportar(_datos_minimos())
    assert isinstance(contenido, bytes)
    assert len(contenido) > 0
    assert contenido[:2] == b"PK"  # firma ZIP de los .xlsx
    assert media_type == MIME_XLSX
    assert ext == "xlsx"


def test_exportadores_toleran_datos_vacios():
    # Todas las claves se leen con .get(): un dict vacío no debe romper
    for formato in ("pdf", "xlsx"):
        contenido, _, _ = ExportadorReporteFactory.crear(formato).exportar({})
        assert len(contenido) > 0
