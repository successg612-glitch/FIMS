import csv
import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

COLUMN_HEADERS = ["File", "Change", "Timestamp (UTC)"]


def alerts_to_csv_bytes(alerts):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["filepath", "change_type", "timestamp"])
    for alert in alerts:
        writer.writerow([alert.get("filepath", ""), alert.get("change_type", "unknown"), alert.get("timestamp", "")])
    return buffer.getvalue().encode("utf-8")


def alerts_to_pdf_bytes(alerts):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="FIMS Alert Log")
    styles = getSampleStyleSheet()

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    elements = [
        Paragraph("File Integrity Monitoring System - Alert Log", styles["Title"]),
        Paragraph(f"Generated {generated_at} - {len(alerts)} alert(s)", styles["Normal"]),
        Spacer(1, 16),
    ]

    rows = [COLUMN_HEADERS] + [
        [
            alert.get("filepath", ""),
            alert.get("change_type", "unknown").capitalize(),
            alert.get("timestamp", "")[:19].replace("T", " "),
        ]
        for alert in alerts
    ]
    table = Table(rows, colWidths=[300, 90, 120], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b0b0b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f2")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
