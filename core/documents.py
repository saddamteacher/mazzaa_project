"""Генерация прайс-листов и коммерческих предложений в Excel и PDF из одной таблицы данных."""
import re
from io import BytesIO
from pathlib import Path

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE = Path(__file__).resolve().parent
LOGO = BASE.parent / "static" / "img" / "logo.jpg"
RED = "E5171E"

pdfmetrics.registerFont(TTFont("DejaVu", str(BASE / "fonts" / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(BASE / "fonts" / "DejaVuSans-Bold.ttf")))


def _cell(value):
    return "" if value is None else value


def render_xlsx(doc):
    """doc: {title, meta: [str], headers: [str], rows: [[...]], totals: [[...]], notes: [str]}"""
    wb = Workbook()
    ws = wb.active
    ws.title = re.sub(r"[\\/*?:\[\]]", " ", doc["title"])[:30]
    ws.append([doc["title"]])
    ws["A1"].font = Font(bold=True, size=16, color=RED)
    for line in doc["meta"]:
        ws.append([line])
    ws.append([])
    ws.append(doc["headers"])
    head_row = ws.max_row
    thin = Side(style="thin", color="999999")
    for cell in ws[head_row]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=RED)
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        cell.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    for row in doc["rows"] + doc.get("totals", []):
        ws.append([_cell(v) for v in row])
        for cell in ws[ws.max_row]:
            cell.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    for i in range(len(doc.get("totals", []))):
        for cell in ws[ws.max_row - i]:
            cell.font = Font(bold=True)
    ws.append([])
    for line in doc.get("notes", []):
        ws.append([line])
    for i, _ in enumerate(doc["headers"], start=1):
        width = max(len(str(_cell(r[i - 1]))) for r in [doc["headers"]] + doc["rows"]) + 3
        ws.column_dimensions[get_column_letter(i)].width = min(max(width, 10), 60)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _fmt(value):
    if value is None:
        return "—"
    if isinstance(value, (int, str)):
        return str(value)
    return f"{float(value):,.2f}".replace(",", " ").rstrip("0").rstrip(".") if float(value) % 1 else f"{int(value):,}".replace(",", " ")


def render_pdf(doc):
    buf = BytesIO()
    pdf = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                            topMargin=10 * mm, bottomMargin=10 * mm, title=doc["title"])
    normal = ParagraphStyle("n", fontName="DejaVu", fontSize=9, leading=12)
    small = ParagraphStyle("s", parent=normal, fontSize=8, textColor=colors.HexColor("#555555"))
    title = ParagraphStyle("t", fontName="DejaVu-Bold", fontSize=15, leading=19, textColor=colors.white)
    cell = ParagraphStyle("c", parent=normal, fontSize=8.5, leading=10.5)

    header = Table([[Image(str(LOGO), width=44 * mm, height=27 * mm), Paragraph(doc["title"], title)]],
                   colWidths=[50 * mm, pdf.width - 50 * mm])
    header.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.black),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story = [header, Spacer(1, 4 * mm)]
    story += [Paragraph(line, normal) for line in doc["meta"]]
    story.append(Spacer(1, 4 * mm))

    totals = doc.get("totals", [])
    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle("h", parent=cell, textColor=colors.white)) for h in doc["headers"]]]
    for row in doc["rows"] + totals:
        data.append([Paragraph(_fmt(v) if i else str(_cell(v)), cell) for i, v in enumerate(row)])
    name_col = doc.get("wide_col", 1)
    rest = (pdf.width - 85 * mm) / (len(doc["headers"]) - 1)
    widths = [85 * mm if i == name_col else rest for i in range(len(doc["headers"]))]
    table = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#" + RED)),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF4E0")]),
    ]
    if totals:
        style.append(("BACKGROUND", (0, -len(totals)), (-1, -1), colors.HexColor("#FFD400")))
    table.setStyle(TableStyle(style))
    story += [table, Spacer(1, 4 * mm)]
    story += [Paragraph(line, small) for line in doc.get("notes", [])]
    pdf.build(story)
    return buf.getvalue()


def file_response(doc, fmt, filename):
    if fmt == "xlsx":
        body, ctype = render_xlsx(doc), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        fmt = "pdf"
        body, ctype = render_pdf(doc), "application/pdf"
    response = HttpResponse(body, content_type=ctype)
    response["Content-Disposition"] = f'attachment; filename="{filename}.{fmt}"'
    return response
