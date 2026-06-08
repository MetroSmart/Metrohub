from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

from app.export.base import ExportadorReporte

_AZUL_OSC  = colors.HexColor("#042C53")
_AZUL_MED  = colors.HexColor("#185FA5")
_AZUL_CLR  = colors.HexColor("#E6F1FB")
_WARN      = colors.HexColor("#FAEEDA")
_WARN_BRD  = colors.HexColor("#F0D1A0")
_DANGER    = colors.HexColor("#FCEBEB")
_OK        = colors.HexColor("#EAF3DE")
_GRIS      = colors.HexColor("#F4F6F8")
_GRIS_BRD  = colors.HexColor("#CCCCCC")
_TEXTO     = colors.HexColor("#1A1A1A")


def _tbl_style_base(header_color=None) -> TableStyle:
    hc = header_color or _AZUL_OSC
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), hc),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_GRIS, colors.white]),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, _GRIS_BRD),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ])


_ESTADO_COLORES = {
    "operativo": _OK,
    "aprobada":  _OK,
    "activo":    _OK,
    "mantenimiento": _WARN,
    "revision":  _WARN,
    "borrador":  _GRIS,
    "baja":      _DANGER,
    "reparacion":_WARN,
}


class PdfExporter(ExportadorReporte):
    def exportar(self, datos: dict[str, Any]) -> tuple[bytes, str, str]:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )
        styles = getSampleStyleSheet()
        story = []

        title_s = ParagraphStyle("mh_title", parent=styles["Heading1"],
            fontSize=20, alignment=TA_CENTER, spaceAfter=2, textColor=_AZUL_OSC)
        sub_s = ParagraphStyle("mh_sub", parent=styles["Normal"],
            fontSize=9, alignment=TA_CENTER, spaceAfter=6, textColor=colors.HexColor("#555"))
        h2_s = ParagraphStyle("mh_h2", parent=styles["Heading2"],
            fontSize=11, spaceBefore=16, spaceAfter=5, textColor=_AZUL_MED)
        h2_warn_s = ParagraphStyle("mh_h2w", parent=styles["Heading2"],
            fontSize=11, spaceBefore=16, spaceAfter=5, textColor=colors.HexColor("#854F0B"))
        note_s = ParagraphStyle("mh_note", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#888"), spaceAfter=4)

        # ── Portada ──────────────────────────────────────────────────
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("MetroHub", title_s))
        story.append(Paragraph(
            f"Informe Operativo ATU &nbsp;·&nbsp; Metropolitano de Lima",
            sub_s,
        ))
        story.append(Paragraph(f"Fecha de generación: <b>{datos.get('fecha', '')}</b>", sub_s))
        story.append(HRFlowable(width="100%", thickness=1, color=_AZUL_MED, spaceAfter=14))

        # ── 1. Resumen Ejecutivo (KPIs) ───────────────────────────────
        kpis = datos.get("kpis", {})
        if kpis:
            story.append(Paragraph("1. Resumen Ejecutivo", h2_s))
            _KPI_LABELS = {
                "rutas_activas":         "Rutas activas",
                "choferes_activos":      "Choferes activos",
                "buses_operativos":      "Buses operativos",
                "asignaciones_hoy":      "Asignaciones confirmadas hoy",
                "conflictos_abiertos":   "Conflictos abiertos",
                "certif_por_vencer_30d": "Certificaciones por vencer (30 días)",
            }
            tdata = [["Indicador", "Valor"]]
            for k, v in kpis.items():
                tdata.append([_KPI_LABELS.get(k, k.replace("_", " ").capitalize()), str(v)])
            tbl = Table(tdata, colWidths=[12*cm, 3.5*cm])
            tbl.setStyle(_tbl_style_base())
            tbl.setStyle(TableStyle([
                *_tbl_style_base()._cmds,
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ]))
            story.append(tbl)

        # ── 2. Rutas Activas ─────────────────────────────────────────
        rutas = datos.get("rutas", [])
        story.append(Paragraph(f"2. Rutas Activas ({len(rutas)})", h2_s))
        if rutas:
            tdata = [["Código", "Nombre", "Tipo", "Inicio", "Fin", "Frec. (min)"]]
            for r in rutas:
                tdata.append([r["codigo"], r["nombre"], r["tipo"],
                               r["hora_inicio"], r["hora_fin"], str(r["frecuencia_min"])])
            tbl = Table(tdata, colWidths=[2*cm, 5.5*cm, 2.5*cm, 1.8*cm, 1.8*cm, 2*cm])
            tbl.setStyle(_tbl_style_base())
            story.append(tbl)
        else:
            story.append(Paragraph("Sin rutas activas registradas.", note_s))

        # ── 3. Estado de la Flota ────────────────────────────────────
        buses = datos.get("buses", [])
        story.append(Paragraph(f"3. Estado de la Flota ({len(buses)} unidades)", h2_s))
        if buses:
            tdata = [["Placa", "Tipo", "Año", "Capacidad", "Estado"]]
            tbl_style = _tbl_style_base(_AZUL_MED)
            row_cmds = []
            for i, b in enumerate(buses, start=1):
                tdata.append([b["placa"], b["tipo"], str(b["anio"]),
                               str(b["capacidad"]), b["estado"]])
                bg = _ESTADO_COLORES.get(b["estado"])
                if bg:
                    row_cmds.append(("BACKGROUND", (4, i), (4, i), bg))
            tbl = Table(tdata, colWidths=[2.5*cm, 3.5*cm, 2*cm, 2.5*cm, 4*cm])
            tbl.setStyle(TableStyle([*_tbl_style_base(_AZUL_MED)._cmds, *row_cmds]))
            story.append(tbl)
        else:
            story.append(Paragraph("Sin buses registrados.", note_s))

        # ── 4. Choferes Activos ──────────────────────────────────────
        choferes = datos.get("choferes", [])
        story.append(Paragraph(f"4. Choferes Activos ({len(choferes)})", h2_s))
        if choferes:
            tdata = [["Nombre", "Licencia", "N° Licencia", "Vence Licencia", "Vence Certif."]]
            for c in choferes:
                tdata.append([c["nombre"], c["licencia"], c["numero"],
                               c["vence_lic"], c["vence_certif"]])
            tbl = Table(tdata, colWidths=[4.5*cm, 2*cm, 3*cm, 2.8*cm, 2.8*cm])
            tbl.setStyle(_tbl_style_base())
            story.append(tbl)
        else:
            story.append(Paragraph("Sin choferes activos registrados.", note_s))

        # ── 5. Alertas de Documentos ─────────────────────────────────
        alertas = datos.get("alertas_doc", [])
        story.append(Paragraph(
            f"5. Alertas de Documentos — próximos 30 días ({len(alertas)})",
            h2_warn_s if alertas else h2_s,
        ))
        if alertas:
            tdata = [["Chofer", "Vence Licencia", "Días rest.", "Vence Certif.", "Días rest."]]
            row_cmds = []
            for i, a in enumerate(alertas, start=1):
                d_lic = a["dias_lic"]
                d_cer = a["dias_certif"]
                tdata.append([a["nombre"], a["vence_lic"], str(d_lic),
                               a["vence_certif"], str(d_cer)])
                if d_lic <= 7 or d_cer <= 7:
                    row_cmds.append(("BACKGROUND", (0, i), (-1, i), _DANGER))
                elif d_lic <= 30 or d_cer <= 30:
                    row_cmds.append(("BACKGROUND", (0, i), (-1, i), _WARN))
            tbl = Table(tdata, colWidths=[4.5*cm, 2.8*cm, 1.8*cm, 2.8*cm, 1.8*cm])
            tbl.setStyle(TableStyle([*_tbl_style_base(colors.HexColor("#854F0B"))._cmds, *row_cmds]))
            story.append(tbl)
        else:
            story.append(Paragraph("Sin vencimientos próximos.", note_s))

        # ── 6. Programaciones Vigentes ───────────────────────────────
        progs = datos.get("programaciones", [])
        story.append(Paragraph(f"6. Programaciones Vigentes ({len(progs)})", h2_s))
        if progs:
            tdata = [["Nombre", "Estado", "Inicio", "Fin"]]
            row_cmds = []
            for i, p in enumerate(progs, start=1):
                tdata.append([p["nombre"], p["estado"], p["inicio"], p["fin"]])
                bg = _ESTADO_COLORES.get(p["estado"])
                if bg:
                    row_cmds.append(("BACKGROUND", (1, i), (1, i), bg))
            tbl = Table(tdata, colWidths=[6*cm, 2.8*cm, 2.5*cm, 2.5*cm])
            tbl.setStyle(TableStyle([*_tbl_style_base()._cmds, *row_cmds]))
            story.append(tbl)
        else:
            story.append(Paragraph("Sin programaciones vigentes.", note_s))

        # ── 7. Conflictos Abiertos ───────────────────────────────────
        conflictos = datos.get("conflictos", [])
        story.append(Paragraph(
            f"7. Conflictos Abiertos ({len(conflictos)})",
            h2_warn_s if conflictos else h2_s,
        ))
        if conflictos:
            tdata = [["Tipo", "Descripción"]]
            for c in conflictos:
                tdata.append([c["tipo"], c["descripcion"]])
            tbl = Table(tdata, colWidths=[4.5*cm, 11*cm])
            tbl.setStyle(_tbl_style_base(colors.HexColor("#A32D2D")))
            story.append(tbl)
        else:
            story.append(Paragraph("Sin conflictos abiertos. ✓", note_s))

        # ── Pie ──────────────────────────────────────────────────────
        story.append(Spacer(1, 0.8*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=_GRIS_BRD, spaceAfter=6))
        story.append(Paragraph(
            "MetroHub — Autoridad de Transporte Urbano (ATU) · Documento generado automáticamente",
            ParagraphStyle("foot", parent=styles["Normal"],
                fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor("#AAAAAA")),
        ))

        doc.build(story)
        return buffer.getvalue(), "application/pdf", "pdf"
