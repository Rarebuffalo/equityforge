"""LLM-based structured financial data extraction."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime

from openai import OpenAI

from app.core.config import settings
from app.models.schema import EquityResearchReport

EXTRACTION_SYSTEM_PROMPT = """You are an equity research analyst assistant. Extract financial and business
information from the provided company document text.

CRITICAL RULES:
1. NEVER hallucinate or invent data. If a field is not present in the document, use null.
2. Return ONLY valid JSON matching the schema exactly.
3. Extract actual numbers and percentages as strings with their units (e.g. "7,167", "70.4%", "Rs. 337").
4. For financial time series, populate the "financials" object with numeric arrays (use null for missing years).
5. Write professional analyst-style narrative for outlook_valuation, investment_thesis, and analyst_summary
   based ONLY on document content.
6. key_highlights and risks should be bullet-style strings derived from the document.
7. Use "Not Available" only when the document explicitly states unavailability; otherwise use null.
"""

EXTRACTION_USER_TEMPLATE = """Company Name (user provided): {company_name}

Document Content:
---
{document_text}
---

Extract all available information into this JSON schema:
{{
  "company_name": "string",
  "sector": "string or null",
  "industry": "string or null",
  "report_date": "string or null (e.g. 29th July, 2025)",
  "data_as_of": "string or null",
  "headline": "string or null (analyst headline)",
  "rating": "BUY|HOLD|SELL|ACCUMULATE|REDUCE or null",
  "target_price": "string or null",
  "cmp": "string or null",
  "expected_return": "string or null",
  "stock_type": "string or null",
  "bloomberg_code": "string or null",
  "nse_code": "string or null",
  "bse_code": "string or null",
  "result_update_label": "string or null (e.g. Q2FY26 Result Update)",
  "business_overview": "string or null",
  "key_highlights": ["string"],
  "investment_thesis": "string or null",
  "outlook_valuation": "string or null",
  "industry_outlook": "string or null",
  "risks": ["string"],
  "analyst_summary": "string or null",
  "company_data": {{
    "market_cap": "string or null",
    "week_52_high_low": "string or null",
    "enterprise_value": "string or null",
    "outstanding_shares": "string or null",
    "free_float": "string or null",
    "dividend_yield": "string or null",
    "avg_volume_6m": "string or null",
    "beta": "string or null",
    "face_value": "string or null"
  }},
  "shareholding": [{{"period": "Q1FY26", "promoters": "0.0", "fiis": "47.3"}}],
  "price_performance": [{{"period": "1 Year", "absolute_return": "39.7%"}}],
  "quarterly_financials": [
    {{"metric": "Sales", "current_q": "7167", "previous_year_q": "4206", "yoy_growth": "70.4", "previous_q": "5833", "qoq_growth": "22.9"}}
  ],
  "quarterly_period_current": "Q1FY26",
  "quarterly_period_previous_year": "Q1FY25",
  "quarterly_period_previous_q": "Q4FY25",
  "annual_estimates": [
    {{"metric": "Sales", "fy25a": "20243", "fy26e": "35020", "fy27e": "54632"}}
  ],
  "annual_estimate_years": ["FY25A", "FY26E", "FY27E"],
  "historical_pl": [{{"metric": "Sales", "values": ["7079", "12114", "20243"]}}],
  "historical_pl_years": ["FY23A", "FY24A", "FY25A"],
  "historical_bs": [],
  "historical_bs_years": [],
  "historical_cf": [],
  "historical_cf_years": [],
  "ratios": [{{"category": "Profitability", "metric": "EBITDA margin (%)", "values": ["-17.1", "0.3", "3.1"]}}],
  "ratio_years": ["FY23A", "FY24A", "FY25A"],
  "financials": {{
    "revenue": [7079, 12114, 20243],
    "ebitda": [-1210, 42, 637],
    "net_profit": [-971, 351, 527],
    "eps": [-1.2, 0.4, 0.6]
  }},
  "financial_years": ["FY23A", "FY24A", "FY25A"]
}}
"""


def extract_report_data(company_name: str, document_text: str) -> EquityResearchReport:
    openai_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY", "")
    gemini_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    if settings.mock_llm or (not openai_key and not gemini_key):
        return _mock_extract(company_name, document_text)

    if openai_key:
        client = OpenAI(api_key=openai_key)
        model = settings.openai_model
    else:
        # Use OpenAI-compatible endpoint for Google Gemini API
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        model = settings.gemini_model or "gemini-2.5-flash"

    truncated = document_text[:120_000]

    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": EXTRACTION_USER_TEMPLATE.format(
                        company_name=company_name,
                        document_text=truncated,
                    ),
                },
            ],
            temperature=0.1,
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        data["company_name"] = company_name

        if not data.get("report_date"):
            data["report_date"] = datetime.now().strftime("%d %B, %Y")

        return EquityResearchReport.model_validate(data)
    except Exception as exc:
        print(f"[LLM Extractor] API call failed ({exc}). Falling back to heuristic extraction.")
        return _mock_extract(company_name, document_text)


def _mock_extract(company_name: str, document_text: str) -> EquityResearchReport:
    """Heuristic extraction when LLM is unavailable (dev/demo)."""
    text = document_text[:8000]

    revenue = _find_numbers_after_keywords(text, ["revenue", "sales", "top line"], limit=5)
    profit = _find_numbers_after_keywords(text, ["net profit", "pat", "profit after tax"], limit=5)
    ebitda_vals = _find_numbers_after_keywords(text, ["ebitda"], limit=5)

    highlights = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("•") or line.startswith("-") or line.startswith("*"):
            highlights.append(line.lstrip("•-* ").strip())
        elif re.search(r"\d+\.?\d*\s*%", line) and len(line) > 30:
            highlights.append(line[:300])
    highlights = highlights[:8]

    sector_match = re.search(
        r"(?:sector|industry)\s*[:\-]?\s*([^\n,]+)", text, re.IGNORECASE
    )

    return EquityResearchReport(
        company_name=company_name,
        sector=sector_match.group(1).strip() if sector_match else None,
        report_date=datetime.now().strftime("%d %B, %Y"),
        data_as_of=datetime.now().strftime("%d-%B-%Y, %H:%Mhrs"),
        headline=f"{company_name} — Financial Performance Update",
        rating="HOLD",
        result_update_label="Result Update",
        business_overview=text[:800] if text else None,
        key_highlights=highlights or ["Financial data extracted from uploaded document."],
        investment_thesis=(
            f"Based on the uploaded financial context, {company_name} shows "
            "operational trends that warrant further analysis. "
            "Refer to financial tables for detailed metrics."
        ),
        outlook_valuation=(
            f"{company_name} operates in a dynamic market environment. "
            "Valuation and outlook should be assessed alongside latest quarterly results."
        ),
        industry_outlook="Industry trends referenced in the source document apply.",
        risks=["Market volatility", "Regulatory changes", "Competitive pressures"],
        analyst_summary=(
            f"We maintain a neutral stance on {company_name} pending further data. "
            "Key financial metrics are summarized in this report."
        ),
        quarterly_financials=[
            {
                "metric": "Sales",
                "current_q": str(revenue[0]) if revenue else None,
                "previous_year_q": str(revenue[1]) if len(revenue) > 1 else None,
                "yoy_growth": None,
            },
            {
                "metric": "EBITDA",
                "current_q": str(ebitda_vals[0]) if ebitda_vals else None,
                "previous_year_q": str(ebitda_vals[1]) if len(ebitda_vals) > 1 else None,
                "yoy_growth": None,
            },
            {
                "metric": "Reported PAT",
                "current_q": str(profit[0]) if profit else None,
                "previous_year_q": str(profit[1]) if len(profit) > 1 else None,
                "yoy_growth": None,
            },
        ],
        annual_estimates=[
            {
                "metric": "Sales",
                "fy25a": str(revenue[0]) if revenue else None,
                "fy26e": str(revenue[1]) if len(revenue) > 1 else None,
                "fy27e": str(revenue[2]) if len(revenue) > 2 else None,
            },
            {
                "metric": "EBITDA",
                "fy25a": str(ebitda_vals[0]) if ebitda_vals else None,
                "fy26e": str(ebitda_vals[1]) if len(ebitda_vals) > 1 else None,
                "fy27e": str(ebitda_vals[2]) if len(ebitda_vals) > 2 else None,
            },
            {
                "metric": "PAT Adjusted",
                "fy25a": str(profit[0]) if profit else None,
                "fy26e": str(profit[1]) if len(profit) > 1 else None,
                "fy27e": str(profit[2]) if len(profit) > 2 else None,
            },
        ],
        annual_estimate_years=["FY25A", "FY26E", "FY27E"],
        financials={
            "revenue": revenue[:5] or [],
            "ebitda": ebitda_vals[:5] or [],
            "net_profit": profit[:5] or [],
        },
        financial_years=[f"Y{i+1}" for i in range(max(len(revenue), len(profit), 1))],
    )


def _find_numbers_after_keywords(text: str, keywords: list[str], limit: int = 5) -> list[float]:
    numbers: list[float] = []
    for keyword in keywords:
        for match in re.finditer(keyword, text, re.IGNORECASE):
            snippet = text[match.end() : match.end() + 120]
            for num_match in re.finditer(r"[\d,]+\.?\d*", snippet):
                try:
                    val = float(num_match.group().replace(",", ""))
                    if val > 0 and val not in numbers:
                        numbers.append(val)
                except ValueError:
                    continue
                if len(numbers) >= limit:
                    return numbers
    return numbers[:limit]
