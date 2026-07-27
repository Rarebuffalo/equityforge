"""Render HTML report template and convert to PDF via WeasyPrint."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.models.schema import EquityResearchReport

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def render_pdf(report: EquityResearchReport) -> bytes:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("report.html")
    html_content = template.render(report=report)

    css_path = STATIC_DIR / "report.css"
    html = HTML(string=html_content, base_url=str(STATIC_DIR))
    pdf_bytes = html.write_pdf(stylesheets=[str(css_path)])
    return pdf_bytes
