from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.platypus.flowables import KeepTogether

from app.export.base import ExportadorReporte

# ── Paleta ────────────────────────────────────────────────────────────
_NAVY      = colors.HexColor("#0A1F3D")
_AZUL_OSC  = colors.HexColor("#042C53")
_AZUL_MED  = colors.HexColor("#185FA5")
_AZUL_CLR  = colors.HexColor("#D6E8F7")
_PLATA     = colors.HexColor("#8FA8C8")
_WARN      = colors.HexColor("#FDF3E3")
_WARN_BRD  = colors.HexColor("#E8A44A")
_DANGER    = colors.HexColor("#FDF0F0")
_DANGER_BRD= colors.HexColor("#D94040")
_OK        = colors.HexColor("#EBF5E1")
_OK_BRD    = colors.HexColor("#5A9E2F")
_GRIS_CLR  = colors.HexColor("#F2F4F7")
_GRIS_BRD  = colors.HexColor("#C8CFD8")
_TEXTO     = colors.HexColor("#0D1B2A")
_TEXTO_SUB = colors.HexColor("#4A5568")
_BLANCO    = colors.white


def _pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(_AZUL_OSC)
    canvas.rect(0, 0, A4[0], 1.1*cm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(_PLATA)
    canvas.drawString(2*cm, 0.38*cm,
        "MetroHub — Autoridad de Transporte Urbano (ATU)  ·  Documento generado automáticamente")
    canvas.setFillColor(_BLANCO)
    canvas.drawRightString(A4[0] - 2*cm, 0.38*cm, f"Página {doc.page}")
    canvas.restoreState()


def _encabezado_pagina(canvas, doc):
    _pie_pagina(canvas, doc)
    if doc.page > 1:
        canvas.saveState()
        canvas.setFillColor(_AZUL_OSC)
        canvas.rect(0, A4[1] - 1.1*cm, A4[0], 1.1*cm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(_PLATA)
        canvas.drawString(2*cm, A4[1] - 0.72*cm, "MetroHub  ·  Informe Operativo ATU")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(A4[0] - 2*cm, A4[1] - 0.72*cm,
            f"Fecha: {getattr(doc, '_fecha_reporte', '')}")
        canvas.restoreState()


def _tbl_header_style(hc=None) -> list:
    hc = hc or _AZUL_OSC
    return [
        ("BACKGROUND",    (0, 0), (-1, 0), hc),
        ("TEXTCOLOR",     (0, 0), (-1, 0), _BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 7.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_GRIS_CLR, _BLANCO]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
        ("GRID",          (0, 0), (-1, -1), 0.25, _GRIS_BRD),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.5, _AZUL_MED),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]


def _make_tbl(data, widths, hc=None, extra_cmds=None):
    tbl = Table(data, colWidths=widths)
    cmds = _tbl_header_style(hc) + (extra_cmds or [])
    tbl.setStyle(TableStyle(cmds))
    return tbl


def _seccion_titulo(texto: str, styles, warn=False):
    color = colors.HexColor("#8B3A0F") if warn else _AZUL_OSC
    bg    = colors.HexColor("#FEF3EC") if warn else _AZUL_CLR
    tbl = Table([[Paragraph(texto,
        ParagraphStyle("sh", parent=styles["Normal"],
            fontSize=10, fontName="Helvetica-Bold",
            textColor=color, spaceAfter=0, spaceBefore=0))
    ]], colWidths=[16.2*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LINEAFTER",     (0,0), (0,-1), 3, color),
        ("LINEBEFORE",    (0,0), (0,-1), 3, color),
    ]))
    return tbl


_ESTADO_COLORES = {
    "operativo":    (_OK,     _OK_BRD),
    "aprobada":     (_OK,     _OK_BRD),
    "activo":       (_OK,     _OK_BRD),
    "mantenimiento":(_WARN,   _WARN_BRD),
    "revision":     (_WARN,   _WARN_BRD),
    "borrador":     (_GRIS_CLR, _GRIS_BRD),
    "baja":         (_DANGER, _DANGER_BRD),
    "reparacion":   (_WARN,   _WARN_BRD),
    "suspendido":   (_DANGER, _DANGER_BRD),
}


class PdfExporter(ExportadorReporte):
    def exportar(self, datos: dict[str, Any]) -> tuple[bytes, str, str]:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=1.9*cm, rightMargin=1.9*cm,
            topMargin=1.8*cm, bottomMargin=1.6*cm,
        )
        doc._fecha_reporte = datos.get("fecha", "")
        styles = getSampleStyleSheet()

        note_s = ParagraphStyle("note", parent=styles["Normal"],
            fontSize=8, textColor=_TEXTO_SUB, spaceAfter=4, leftIndent=4)
        cell_s = ParagraphStyle("cell", parent=styles["Normal"],
            fontSize=7.5, textColor=_TEXTO, leading=10)

        story = []

        # ══ PORTADA ════════════════════════════════════════════════════
        # Banda superior oscura
        header_data = [[
            Paragraph(
                '<font color="white"><b>METROHUB</b></font>',
                ParagraphStyle("ht", parent=styles["Normal"],
                    fontSize=22, fontName="Helvetica-Bold",
                    textColor=_BLANCO, spaceAfter=0, spaceBefore=0)),
            Paragraph(
                f'<font color="#8FA8C8">Fecha:&nbsp;</font>'
                f'<font color="white"><b>{datos.get("fecha","")}</b></font>',
                ParagraphStyle("hd", parent=styles["Normal"],
                    fontSize=9, textColor=_PLATA, alignment=TA_RIGHT,
                    spaceAfter=0, spaceBefore=0)),
        ]]
        header_tbl = Table(header_data, colWidths=[10*cm, 6.2*cm])
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), _NAVY),
            ("LEFTPADDING",   (0,0), (-1,-1), 16),
            ("RIGHTPADDING",  (0,0), (-1,-1), 16),
            ("TOPPADDING",    (0,0), (-1,-1), 18),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
        ]))
        story.append(header_tbl)

        sub_data = [[
            Paragraph(
                'Informe Operativo ATU &nbsp;·&nbsp; Metropolitano de Lima',
                ParagraphStyle("hs", parent=styles["Normal"],
                    fontSize=9, textColor=_PLATA,
                    spaceAfter=0, spaceBefore=0)),
        ]]
        sub_tbl = Table(sub_data, colWidths=[16.2*cm])
        sub_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), _NAVY),
            ("LEFTPADDING",   (0,0), (-1,-1), 16),
            ("RIGHTPADDING",  (0,0), (-1,-1), 16),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 14),
            ("LINEBELOW",     (0,0), (-1,-1), 3, _AZUL_MED),
        ]))
        story.append(sub_tbl)
        story.append(Spacer(1, 0.5*cm))

        # ══ 1. KPIs ════════════════════════════════════════════════════
        kpis = datos.get("kpis", {})
        if kpis:
            story.append(_seccion_titulo("1. Resumen Ejecutivo", styles))
            story.append(Spacer(1, 0.2*cm))
            _KPI_LABELS = {
                "rutas_activas":         "Rutas activas",
                "choferes_activos":      "Choferes activos",
                "buses_operativos":      "Buses operativos",
                "asignaciones_hoy":      "Asignaciones confirmadas hoy",
                "conflictos_abiertos":   "Conflictos abiertos",
                "certif_por_vencer_30d": "Certificaciones por vencer (30 días)",
            }
            kpi_items = [(k, v) for k, v in kpis.items()]
            mid = (len(kpi_items) + 1) // 2
            left, right = kpi_items[:mid], kpi_items[mid:]
            rows = []
            for i in range(mid):
                lk, lv = left[i]
                rk, rv = right[i] if i < len(right) else ("", "")
                rows.append([
                    Paragraph(_KPI_LABELS.get(lk, lk.replace("_"," ").capitalize()), cell_s),
                    Paragraph(f"<b>{lv}</b>", ParagraphStyle("kv", parent=cell_s,
                        alignment=TA_CENTER, textColor=_AZUL_OSC, fontName="Helvetica-Bold")),
                    Paragraph(_KPI_LABELS.get(rk, rk.replace("_"," ").capitalize()) if rk else "", cell_s),
                    Paragraph(f"<b>{rv}</b>" if rv != "" else "", ParagraphStyle("kv2", parent=cell_s,
                        alignment=TA_CENTER, textColor=_AZUL_OSC, fontName="Helvetica-Bold")),
                ])
            kpi_tbl = Table(rows, colWidths=[6*cm, 1.8*cm, 6*cm, 1.8*cm])
            kpi_cmds = [
                ("BACKGROUND",   (0,0), (-1,-1), _GRIS_CLR),
                ("ROWBACKGROUNDS",(0,0),(-1,-1), [_AZUL_CLR, _GRIS_CLR]),
                ("GRID",         (0,0), (-1,-1), 0.25, _GRIS_BRD),
                ("LINEAFTER",    (1,0), (1,-1), 1, _GRIS_BRD),
                ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING",   (0,0), (-1,-1), 6),
                ("BOTTOMPADDING",(0,0), (-1,-1), 6),
                ("LEFTPADDING",  (0,0), (-1,-1), 10),
                ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ]
            kpi_tbl.setStyle(TableStyle(kpi_cmds))
            story.append(kpi_tbl)
            story.append(Spacer(1, 0.35*cm))

        # ══ 2. Rutas ═══════════════════════════════════════════════════
        rutas = datos.get("rutas", [])
        story.append(_seccion_titulo(f"2. Rutas Activas ({len(rutas)})", styles))
        story.append(Spacer(1, 0.2*cm))
        if rutas:
            tdata = [["Código", "Nombre", "Tipo", "Inicio", "Fin", "Frec."]]
            for r in rutas:
                tdata.append([r["codigo"], r["nombre"], r["tipo"],
                               r["hora_inicio"], r["hora_fin"], f"{r['frecuencia_min']} min"])
            story.append(_make_tbl(tdata, [2*cm, 5.5*cm, 2.5*cm, 1.8*cm, 1.8*cm, 2.2*cm]))
        else:
            story.append(Paragraph("Sin rutas activas registradas.", note_s))
        story.append(Spacer(1, 0.35*cm))

        # ══ 3. Flota ═══════════════════════════════════════════════════
        buses = datos.get("buses", [])
        story.append(_seccion_titulo(f"3. Estado de la Flota ({len(buses)} unidades)", styles))
        story.append(Spacer(1, 0.2*cm))
        if buses:
            tdata = [["Placa", "Tipo", "Año", "Capacidad", "Estado"]]
            extra = []
            for i, b in enumerate(buses, start=1):
                tdata.append([b["placa"], b["tipo"], str(b["anio"]),
                               str(b["capacidad"]), b["estado"].capitalize()])
                bg, _ = _ESTADO_COLORES.get(b["estado"], (_GRIS_CLR, _GRIS_BRD))
                extra.append(("BACKGROUND", (4, i), (4, i), bg))
            story.append(_make_tbl(tdata, [2.5*cm, 3.5*cm, 2*cm, 2.5*cm, 4*cm],
                                   hc=_AZUL_MED, extra_cmds=extra))
        else:
            story.append(Paragraph("Sin buses registrados.", note_s))
        story.append(Spacer(1, 0.35*cm))

        # ══ 4. Choferes ════════════════════════════════════════════════
        choferes = datos.get("choferes", [])
        story.append(_seccion_titulo(f"4. Choferes Activos ({len(choferes)})", styles))
        story.append(Spacer(1, 0.2*cm))
        if choferes:
            tdata = [["Apellidos y Nombres", "Tipo Lic.", "N° Licencia", "Vence Lic.", "Vence Certif."]]
            for c in choferes:
                tdata.append([c["nombre"], c["licencia"], c["numero"],
                               c["vence_lic"], c["vence_certif"]])
            story.append(_make_tbl(tdata, [4.8*cm, 2*cm, 3*cm, 2.7*cm, 2.7*cm]))
        else:
            story.append(Paragraph("Sin choferes activos registrados.", note_s))
        story.append(Spacer(1, 0.35*cm))

        # ══ 5. Alertas ═════════════════════════════════════════════════
        alertas = datos.get("alertas_doc", [])
        story.append(_seccion_titulo(
            f"5. Alertas de Documentos — próximos 30 días ({len(alertas)})",
            styles, warn=bool(alertas)))
        story.append(Spacer(1, 0.2*cm))
        if alertas:
            tdata = [["Chofer", "Vence Licencia", "Días", "Vence Certif.", "Días"]]
            extra = []
            for i, a in enumerate(alertas, start=1):
                d_lic, d_cer = a["dias_lic"], a["dias_certif"]
                tdata.append([a["nombre"], a["vence_lic"], str(d_lic),
                               a["vence_certif"], str(d_cer)])
                if d_lic <= 7 or d_cer <= 7:
                    extra.append(("BACKGROUND", (0,i), (-1,i), _DANGER))
                elif d_lic <= 30 or d_cer <= 30:
                    extra.append(("BACKGROUND", (0,i), (-1,i), _WARN))
            story.append(_make_tbl(tdata, [4.5*cm, 2.8*cm, 1.5*cm, 2.8*cm, 1.5*cm],
                                   hc=colors.HexColor("#8B3A0F"), extra_cmds=extra))
        else:
            story.append(Paragraph("Sin vencimientos próximos en los próximos 30 días.", note_s))
        story.append(Spacer(1, 0.35*cm))

        # ══ 6. Programaciones ══════════════════════════════════════════
        progs = datos.get("programaciones", [])
        story.append(_seccion_titulo(f"6. Programaciones Vigentes ({len(progs)})", styles))
        story.append(Spacer(1, 0.2*cm))
        if progs:
            tdata = [["Nombre", "Estado", "Inicio", "Fin"]]
            extra = []
            for i, p in enumerate(progs, start=1):
                tdata.append([p["nombre"], p["estado"].capitalize(), p["inicio"], p["fin"]])
                bg, _ = _ESTADO_COLORES.get(p["estado"], (_GRIS_CLR, _GRIS_BRD))
                extra.append(("BACKGROUND", (1,i), (1,i), bg))
            story.append(_make_tbl(tdata, [6.5*cm, 2.7*cm, 2.5*cm, 2.5*cm], extra_cmds=extra))
        else:
            story.append(Paragraph("Sin programaciones vigentes.", note_s))
        story.append(Spacer(1, 0.35*cm))

        # ══ 7. Conflictos ══════════════════════════════════════════════
        conflictos = datos.get("conflictos", [])
        story.append(_seccion_titulo(
            f"7. Conflictos Abiertos ({len(conflictos)})",
            styles, warn=bool(conflictos)))
        story.append(Spacer(1, 0.2*cm))
        if conflictos:
            tdata = [["Tipo", "Descripción"]]
            for c in conflictos:
                tdata.append([c["tipo"], c["descripcion"]])
            story.append(_make_tbl(tdata, [4.5*cm, 11*cm],
                                   hc=colors.HexColor("#8B1A1A")))
        else:
            story.append(Paragraph("Sin conflictos abiertos registrados.  ✓", note_s))

        story.append(Spacer(1, 1*cm))

        doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_encabezado_pagina)
        return buffer.getvalue(), "application/pdf", "pdf"
