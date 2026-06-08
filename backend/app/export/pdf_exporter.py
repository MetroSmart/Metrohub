from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.export.base import ExportadorReporte

_AZUL_OSC = colors.HexColor("#042C53")
_AZUL_MED = colors.HexColor("#185FA5")
_GRIS     = colors.HexColor("#F4F6F8")
_GRIS_BRD = colors.HexColor("#CCCCCC")


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

        title_style = ParagraphStyle(
            "mh_title", parent=styles["Heading1"],
            fontSize=18, alignment=TA_CENTER, spaceAfter=4,
            textColor=_AZUL_OSC,
        )
        sub_style = ParagraphStyle(
            "mh_sub", parent=styles["Normal"],
            fontSize=9, alignment=TA_CENTER, spaceAfter=20,
            textColor=colors.HexColor("#666666"),
        )
        h2_style = ParagraphStyle(
            "mh_h2", parent=styles["Heading2"],
            fontSize=11, spaceBefore=14, spaceAfter=6,
            textColor=_AZUL_MED,
        )

        story.append(Paragraph("MetroHub — Reporte ATU", title_style))
        story.append(Paragraph(
            f"Metropolitano de Lima &nbsp;·&nbsp; ATU &nbsp;|&nbsp; Fecha: {datos.get('fecha', '')}",
            sub_style,
        ))

        kpis = datos.get("kpis", {})
        if kpis:
            story.append(Paragraph("KPIs Operativos", h2_style))
            story.append(Spacer(1, 4))
            table_data = [["Indicador", "Valor"]]
            for k, v in kpis.items():
                label = k.replace("_", " ").capitalize()
                table_data.append([label, str(v)])
            tbl = Table(table_data, colWidths=[11*cm, 4*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",      (0, 0), (-1, 0), _AZUL_OSC),
                ("TEXTCOLOR",       (0, 0), (-1, 0), colors.white),
                ("FONTNAME",        (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",        (0, 0), (-1, 0), 10),
                ("ROWBACKGROUNDS",  (0, 1), (-1, -1), [_GRIS, colors.white]),
                ("FONTSIZE",        (0, 1), (-1, -1), 9),
                ("GRID",            (0, 0), (-1, -1), 0.3, _GRIS_BRD),
                ("ALIGN",           (1, 0), (1, -1), "CENTER"),
                ("VALIGN",          (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",      (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING",   (0, 0), (-1, -1), 6),
                ("LEFTPADDING",     (0, 0), (-1, -1), 10),
            ]))
            story.append(tbl)

        extras = datos.get("extras", {})
        if extras:
            story.append(Paragraph("Información adicional", h2_style))
            story.append(Spacer(1, 4))
            ext_data = [["Campo", "Valor"]] + [[str(k), str(v)] for k, v in extras.items()]
            ext_tbl = Table(ext_data, colWidths=[11*cm, 4*cm])
            ext_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), _AZUL_MED),
                ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("GRID",          (0, 0), (-1, -1), 0.3, _GRIS_BRD),
                ("ALIGN",         (1, 0), (1, -1), "CENTER"),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ]))
            story.append(ext_tbl)

        doc.build(story)
        return buffer.getvalue(), "application/pdf", "pdf"
