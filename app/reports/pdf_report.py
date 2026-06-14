"""Daily PDF report via reportlab."""

from datetime import date
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PDF_DIR = Path(__file__).parent / "generated" / "pdf"


def pdf_path_for(day: date) -> Path:
    return PDF_DIR / f"badger_cfo_{day.strftime('%Y_%m_%d')}.pdf"


def generate_pdf(report_text: str, day: date | None = None) -> Path:
    """Render the plain-text daily report into a paginated PDF."""
    day = day or date.today()
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    path = pdf_path_for(day)

    c = canvas.Canvas(str(path), pagesize=LETTER)
    width, height = LETTER
    margin = 0.75 * inch
    line_height = 12
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Badger CFO — Boss My Life Report")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Date: {day.isoformat()}")
    y -= 24

    c.setFont("Helvetica", 9)
    for raw_line in report_text.splitlines():
        # crude wrap for long lines
        line = raw_line
        while line:
            chunk, line = line[:110], line[110:]
            if y < margin:
                c.showPage()
                c.setFont("Helvetica", 9)
                y = height - margin
            try:
                c.drawString(margin, y, chunk)
            except Exception:
                # reportlab base fonts can't render some glyphs; degrade gracefully
                c.drawString(margin, y, chunk.encode("latin-1", "replace").decode("latin-1"))
            y -= line_height

    c.save()
    return path
