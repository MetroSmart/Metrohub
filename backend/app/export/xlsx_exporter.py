from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.export.base import ExportadorReporte

_AZUL_OSC  = "042C53"
_AZUL_MED  = "185FA5"
_AZUL_CLR  = "E6F1FB"
_GRIS      = "F4F6F8"
_BORDE_CLR = "CCCCCC"


def _thin_border() -> Border:
    side = Side(style="thin", color=_BORDE_CLR)
    return Border(left=side, right=side, top=side, bottom=side)


class XlsxExporter(ExportadorReporte):
    def exportar(self, datos: dict[str, Any]) -> tuple[bytes, str, str]:
        wb = Workbook()
        ws = wb.active
        ws.title = "KPIs MetroHub"

        # Título
        ws.merge_cells("A1:B1")
        ws["A1"] = f"MetroHub — Reporte ATU · {datos.get('fecha', '')}"
        ws["A1"].font = Font(bold=True, color="FFFFFF", size=13)
        ws["A1"].fill = PatternFill("solid", fgColor=_AZUL_OSC)
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 26

        # Encabezado de tabla
        for col, txt in [(1, "Indicador"), (2, "Valor")]:
            cell = ws.cell(row=2, column=col, value=txt)
            cell.font = Font(bold=True, color=_AZUL_OSC, size=10)
            cell.fill = PatternFill("solid", fgColor=_AZUL_CLR)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = _thin_border()
        ws.row_dimensions[2].height = 20

        # Filas de KPIs
        kpis = datos.get("kpis", {})
        for row_i, (k, v) in enumerate(kpis.items(), start=3):
            label = k.replace("_", " ").capitalize()
            bg = _GRIS if row_i % 2 == 0 else "FFFFFF"

            c_label = ws.cell(row=row_i, column=1, value=label)
            c_label.border = _thin_border()
            c_label.fill = PatternFill("solid", fgColor=bg)
            c_label.font = Font(size=9)

            c_val = ws.cell(row=row_i, column=2, value=v)
            c_val.border = _thin_border()
            c_val.fill = PatternFill("solid", fgColor=bg)
            c_val.alignment = Alignment(horizontal="center")
            c_val.font = Font(size=9)

        # Extras en hoja separada si los hay
        extras = datos.get("extras", {})
        if extras:
            ws2 = wb.create_sheet("Adicional")
            ws2["A1"] = "Campo"
            ws2["B1"] = "Valor"
            for col_cell in [ws2["A1"], ws2["B1"]]:
                col_cell.font = Font(bold=True, color="FFFFFF")
                col_cell.fill = PatternFill("solid", fgColor=_AZUL_MED)
                col_cell.border = _thin_border()
            for row_i, (k, v) in enumerate(extras.items(), start=2):
                ws2.cell(row=row_i, column=1, value=str(k)).border = _thin_border()
                ws2.cell(row=row_i, column=2, value=str(v)).border = _thin_border()
            ws2.column_dimensions["A"].width = 28
            ws2.column_dimensions["B"].width = 20

        ws.column_dimensions[get_column_letter(1)].width = 34
        ws.column_dimensions[get_column_letter(2)].width = 18

        buf = BytesIO()
        wb.save(buf)
        return (
            buf.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        )
