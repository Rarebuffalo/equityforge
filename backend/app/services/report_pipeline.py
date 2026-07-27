"""End-to-end report generation pipeline."""

from __future__ import annotations

from app.models.schema import EquityResearchReport
from app.services.chart_generator import generate_charts
from app.services.document_parser import parse_document
from app.services.llm_extractor import extract_report_data
from app.services.pdf_generator import render_pdf


def generate_report(company_name: str, file_content: bytes, filename: str) -> tuple[bytes, EquityResearchReport]:
    document_text = parse_document(file_content, filename)
    report = extract_report_data(company_name, document_text)
    report = generate_charts(report)
    pdf_bytes = render_pdf(report)
    return pdf_bytes, report
