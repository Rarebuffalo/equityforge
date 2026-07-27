"""Pydantic schema for structured equity research report data."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class CompanyData(BaseModel):
    market_cap: Optional[str] = None
    week_52_high_low: Optional[str] = None
    enterprise_value: Optional[str] = None
    outstanding_shares: Optional[str] = None
    free_float: Optional[str] = None
    dividend_yield: Optional[str] = None
    avg_volume_6m: Optional[str] = None
    beta: Optional[str] = None
    face_value: Optional[str] = None


class ShareholdingRow(BaseModel):
    period: str
    promoters: Optional[str] = None
    fiis: Optional[str] = None
    mfs_institutions: Optional[str] = None
    public: Optional[str] = None
    others: Optional[str] = None


class PricePerformance(BaseModel):
    period: str
    absolute_return: Optional[str] = None
    benchmark_return: Optional[str] = None
    relative_return: Optional[str] = None


class QuarterlyFinancialRow(BaseModel):
    metric: str
    current_q: Optional[str] = None
    previous_year_q: Optional[str] = None
    yoy_growth: Optional[str] = None
    previous_q: Optional[str] = None
    qoq_growth: Optional[str] = None


class AnnualEstimateRow(BaseModel):
    metric: str
    fy25a: Optional[str] = None
    fy26e: Optional[str] = None
    fy27e: Optional[str] = None


class HistoricalFinancialRow(BaseModel):
    metric: str
    values: list[Optional[str]] = Field(default_factory=list)


class RatioRow(BaseModel):
    category: str
    metric: str
    values: list[Optional[str]] = Field(default_factory=list)


class EquityResearchReport(BaseModel):
    """Single source of truth for report rendering."""

    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    report_date: Optional[str] = None
    data_as_of: Optional[str] = None
    headline: Optional[str] = None
    rating: Optional[Literal["BUY", "HOLD", "SELL", "ACCUMULATE", "REDUCE"]] = None
    target_price: Optional[str] = None
    cmp: Optional[str] = None
    expected_return: Optional[str] = None
    stock_type: Optional[str] = None
    bloomberg_code: Optional[str] = None
    nse_code: Optional[str] = None
    bse_code: Optional[str] = None
    time_frame: Optional[str] = "12 Months"
    result_update_label: Optional[str] = None

    business_overview: Optional[str] = None
    key_highlights: list[str] = Field(default_factory=list)
    investment_thesis: Optional[str] = None
    outlook_valuation: Optional[str] = None
    industry_outlook: Optional[str] = None
    risks: list[str] = Field(default_factory=list)
    analyst_summary: Optional[str] = None

    company_data: CompanyData = Field(default_factory=CompanyData)
    shareholding: list[ShareholdingRow] = Field(default_factory=list)
    price_performance: list[PricePerformance] = Field(default_factory=list)

    quarterly_financials: list[QuarterlyFinancialRow] = Field(default_factory=list)
    quarterly_period_current: Optional[str] = None
    quarterly_period_previous_year: Optional[str] = None
    quarterly_period_previous_q: Optional[str] = None

    annual_estimates: list[AnnualEstimateRow] = Field(default_factory=list)
    annual_estimate_years: list[str] = Field(default_factory=list)

    historical_pl: list[HistoricalFinancialRow] = Field(default_factory=list)
    historical_pl_years: list[str] = Field(default_factory=list)
    historical_bs: list[HistoricalFinancialRow] = Field(default_factory=list)
    historical_bs_years: list[str] = Field(default_factory=list)
    historical_cf: list[HistoricalFinancialRow] = Field(default_factory=list)
    historical_cf_years: list[str] = Field(default_factory=list)
    ratios: list[RatioRow] = Field(default_factory=list)
    ratio_years: list[str] = Field(default_factory=list)

    financials: dict[str, list[Optional[float]]] = Field(default_factory=dict)
    financial_years: list[str] = Field(default_factory=list)

    chart_revenue_base64: Optional[str] = None
    chart_profit_base64: Optional[str] = None
    chart_margins_base64: Optional[str] = None
