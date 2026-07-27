"""Parse uploaded documents (PDF, TXT, CSV) into normalized text."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pdfplumber


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv"}


def parse_document(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. Supported: PDF, TXT, CSV."
        )

    if ext == ".pdf":
        return _parse_pdf(content)
    if ext == ".txt":
        return _parse_txt(content)
    return _parse_csv(content)


def _parse_pdf(content: bytes) -> str:
    parts: list[str] = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                parts.append(text.strip())
            tables = page.extract_tables()
            for table in tables or []:
                for row in table:
                    if row:
                        parts.append(" | ".join(str(c or "") for c in row))
    if not parts:
        raise ValueError("Could not extract text from PDF.")
    return "\n\n".join(parts)


def _parse_txt(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            text = content.decode(encoding).strip()
            if text:
                return text
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode text file.")


def _parse_csv(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not decode CSV file.")

    if df.empty:
        raise ValueError("CSV file is empty.")

    lines = [f"Columns: {', '.join(df.columns.astype(str))}"]
    lines.append(df.to_string(index=False))
    return "\n".join(lines)
