# EquityForge System Architecture & Implementation Guide

## Overview

EquityForge is an automated equity research report generator designed to convert unstructured financial documents (PDF, TXT, CSV) into institutional-quality, 4-page equity research reports matching established financial industry standards (Geojit-style).

The application combines artificial intelligence for information extraction and narrative synthesis with deterministic data processing for table formatting, chart generation, and PDF rendering.

---

## High-Level Data Flow

```
+-------------------+
| Input Document    |  (PDF, TXT, CSV)
+---------+---------+
          |
          v
+-------------------+
| Document Parser   |  (pdfplumber / pandas / text decoders)
+---------+---------+
          |  Normalized Text Content
          v
+-------------------+
| Extraction Engine |  (OpenAI GPT-4o / Google Gemini API / Heuristic Mock)
+---------+---------+
          |  Structured JSON Response
          v
+-------------------+
| Pydantic Schema   |  (EquityResearchReport Data Model Validation)
+---------+---------+
          |
     +----+--------------------------------+
     |                                     |
     v                                     v
+-------------------+             +-------------------+
| Chart Generator   |             | Jinja2 Template   |
| (Matplotlib)      |             | (report.html)     |
+---------+---------+             +---------+---------+
          | Base64 PNGs                     | Compiled HTML
          +----------------+----------------+
                           |
                           v
                  +-------------------+
                  | WeasyPrint Engine |
                  +---------+---------+
                            | Rendered PDF
                            v
                  +-------------------+
                  | Download Report   |
                  +-------------------+
```

---

## Detailed Pipeline Component Breakdown

### 1. Document Parsing Engine (`app/services/document_parser.py`)

The parser unifies varied file formats into a clean, normalized string representation before passing it to the AI extraction layer:

- **PDF Documents**: Parsed page-by-page using `pdfplumber`. Text content is extracted alongside tabular structures. Rows inside detected tables are formatted into pipe-delimited text (`Col1 | Col2 | Col3`) to preserve structural relationships for the LLM.
- **TXT Documents**: Text files are decoded sequentially using multiple character encodings (`utf-8`, `latin-1`, `cp1252`) to ensure legacy or non-standard documents parse without decoding errors.
- **CSV Documents**: Tabular CSV data is loaded via `pandas` and serialized into a formatted string including column headers and row data.

---

### 2. Information Extraction Engine (`app/services/llm_extractor.py`)

The extraction layer transforms raw text into structured JSON matching a predefined schema:

- **Dual Provider Support**: Supports both **OpenAI API** (`gpt-4o`) and **Google Gemini API** (`gemini-2.5-flash`) via an OpenAI-compatible interface.
- **Zero-Hallucination Guardrails**: System prompts strictly instruct the LLM never to invent metrics. If a financial figure or section is missing from the input document, the engine returns `null` or `"Not Available"`.
- **Heuristic Development Fallback**: If no API key is provided or `MOCK_LLM=true` is set, the system falls back to a deterministic regex pattern extractor (`_mock_extract`) for offline testing and local development.

---

### 3. Data Validation & Single Source of Truth (`app/models/schema.py`)

The `EquityResearchReport` Pydantic model validates all extracted data before rendering:

- **MetaData**: Company Name, Sector, Industry, Report Date, CMP, Target Price, Rating (`BUY`, `HOLD`, `SELL`, `ACCUMULATE`, `REDUCE`).
- **Narratives**: Business Overview, Key Highlights, Investment Thesis, Outlook & Valuation, Industry Analysis, Risk Factors, Analyst Summary.
- **Tables**: Company Data key-value pairs, Shareholding %, Price Performance, Quarterly Financials, Annual Estimates, Historical P&L, Balance Sheet, Key Ratios.
- **Visuals**: Base64 encoded strings for Revenue, Profit, and Margin charts.

---

### 4. Chart Generation Engine (`app/services/chart_generator.py`)

Financial charts are created programmatically using **Matplotlib** rather than AI generation:

- **Revenue Trend**: Vertical bar chart highlighting historical and estimated top-line performance in Rs. Cr.
- **EBITDA & PAT Growth**: Dual line chart tracking operating profit and net profit trends across reporting periods.
- **Margin Comparison**: Grouped bar chart depicting EBITDA Margin % and Net Margin % side-by-side.
- **Output**: Each chart is rendered in-memory using Matplotlib's `Agg` backend and exported as a clean Base64-encoded PNG string for direct embedding into HTML templates.

---

### 5. Report Template & PDF Renderer (`app/templates/report.html`, `app/static/report.css`, `app/services/pdf_generator.py`)

- **Jinja2 Templating**: Maps fields from the `EquityResearchReport` model directly into structured HTML elements.
- **Geojit Style Layout**:
  - **Page 1**: Header, Rating Badge, Target Price, CMP, Business Overview, Key Highlights, Company Data, Shareholding, Price Performance, Outlook & Valuation, Stock Strip.
  - **Page 2**: Key Highlights, Industry Analysis, Financial Charts Row, Analyst Style Summary, Risk Analysis.
  - **Page 3**: Consolidated Historical P&L, Balance Sheet, and Key Ratios grouped by category.
  - **Page 4**: Investment Rating Criteria, Disclosures, Disclaimer, and Footer Tagline.
- **WeasyPrint PDF Engine**: Converts the rendered HTML and CSS stylesheets into a print-ready A4 PDF document with precise page breaks and running headers/footers.

---

### 6. Web Interface (`frontend/src/app/page.tsx`)

- Built with **Next.js 14** (React, TypeScript, Tailwind CSS).
- Features drag-and-drop file upload, format validation, file size indicators, a 4-stage progress tracker (`Parsing` -> `Extracting` -> `Charting` -> `Rendering PDF`), and instant 1-click PDF download.
- Connects asynchronously to the FastAPI backend (`POST /api/generate-report`) with automatic backend port detection.

---

## Role of the `backend/scripts/` Directory

The `backend/scripts/` directory contains CLI utilities for developer workflow and testing:

- **`generate_examples.py`**: A batch generation script that runs sample documents from `samples/` (PDF, TXT, CSV) through the end-to-end report pipeline and writes output PDF files to `examples/`. It allows developers to test extraction, layout, and PDF rendering without running the web UI server.

---

## Extensibility Guide

1. **Adding a New Field**:
   - Add the attribute to `EquityResearchReport` in `app/models/schema.py`.
   - Update the prompt template in `app/services/llm_extractor.py`.
   - Add the corresponding HTML element in `app/templates/report.html`.

2. **Adding a New Chart Type**:
   - Implement a new plotting function in `app/services/chart_generator.py`.
   - Store the resulting Base64 string in `EquityResearchReport`.
   - Render the `<img>` tag inside `report.html`.
