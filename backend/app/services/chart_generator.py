"""Generate financial charts from structured data using Matplotlib."""

from __future__ import annotations

import base64
import io
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.models.schema import EquityResearchReport

GEOJIT_BLUE = "#1a3a5c"
GEOJIT_ACCENT = "#c0392b"
GEOJIT_GRAY = "#666666"


def _fig_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _safe_series(values: list[Optional[float]]) -> tuple[list[str], list[float]]:
    labels: list[str] = []
    nums: list[float] = []
    for i, v in enumerate(values):
        if v is not None:
            labels.append(f"Y{i+1}")
            nums.append(float(v))
    return labels, nums


def generate_charts(report: EquityResearchReport) -> EquityResearchReport:
    financials = report.financials or {}
    years = report.financial_years or []

    revenue = financials.get("revenue") or []
    ebitda = financials.get("ebitda") or []
    net_profit = financials.get("net_profit") or financials.get("pat") or []

    if revenue:
        labels = years[: len(revenue)] if years else [f"Y{i+1}" for i in range(len(revenue))]
        clean_labels = [str(l) for l in labels]
        clean_vals = [float(v) for v in revenue if v is not None]
        clean_labels = clean_labels[: len(clean_vals)]
        if clean_vals:
            report.chart_revenue_base64 = _revenue_chart(clean_labels, clean_vals)

    if net_profit or ebitda:
        report.chart_profit_base64 = _profit_chart(
            years, ebitda, net_profit
        )

    if revenue and (ebitda or net_profit):
        report.chart_margins_base64 = _margin_chart(years, revenue, ebitda, net_profit)

    return report


def _revenue_chart(labels: list[str], values: list[float]) -> str:
    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.bar(labels, values, color=GEOJIT_BLUE, width=0.55, edgecolor="white")
    ax.set_title("Revenue Trend", fontsize=11, fontweight="bold", color=GEOJIT_BLUE)
    ax.set_ylabel("Rs. Cr", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:,.0f}",
            ha="center",
            va="bottom",
            fontsize=7,
        )
    fig.tight_layout()
    return _fig_to_base64(fig)


def _profit_chart(
    years: list[str],
    ebitda: list[Optional[float]],
    net_profit: list[Optional[float]],
) -> str:
    fig, ax = plt.subplots(figsize=(5, 3))
    n = max(len(ebitda), len(net_profit), 1)
    labels = years[:n] if years else [f"Y{i+1}" for i in range(n)]
    x = range(len(labels))

    if ebitda:
        e_vals = [float(v) if v is not None else 0 for v in ebitda[: len(labels)]]
        ax.plot(labels, e_vals, marker="o", color=GEOJIT_BLUE, linewidth=2, label="EBITDA")

    if net_profit:
        p_vals = [float(v) if v is not None else 0 for v in net_profit[: len(labels)]]
        ax.plot(labels, p_vals, marker="s", color=GEOJIT_ACCENT, linewidth=2, label="PAT")

    ax.set_title("EBITDA & PAT Growth", fontsize=11, fontweight="bold", color=GEOJIT_BLUE)
    ax.set_ylabel("Rs. Cr", fontsize=9)
    ax.legend(fontsize=8, frameon=False)
    ax.tick_params(labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.3, linestyle="--")
    fig.tight_layout()
    return _fig_to_base64(fig)


def _margin_chart(
    years: list[str],
    revenue: list[Optional[float]],
    ebitda: list[Optional[float]],
    net_profit: list[Optional[float]],
) -> str:
    n = min(len(revenue), max(len(ebitda), len(net_profit), 1))
    labels = years[:n] if years else [f"Y{i+1}" for i in range(n)]

    ebitda_margins: list[float] = []
    net_margins: list[float] = []
    for i in range(n):
        rev = revenue[i] if i < len(revenue) else None
        if rev and rev != 0:
            eb = ebitda[i] if i < len(ebitda) and ebitda[i] is not None else None
            np_ = net_profit[i] if i < len(net_profit) and net_profit[i] is not None else None
            ebitda_margins.append((float(eb) / float(rev)) * 100 if eb is not None else 0)
            net_margins.append((float(np_) / float(rev)) * 100 if np_ is not None else 0)

    if not ebitda_margins and not net_margins:
        return ""

    fig, ax = plt.subplots(figsize=(5, 3))
    x = range(len(labels))
    width = 0.35
    if ebitda_margins:
        ax.bar([i - width / 2 for i in x], ebitda_margins, width, label="EBITDA Margin %", color=GEOJIT_BLUE)
    if net_margins:
        ax.bar([i + width / 2 for i in x], net_margins, width, label="Net Margin %", color=GEOJIT_ACCENT)

    ax.set_title("Margin Comparison", fontsize=11, fontweight="bold", color=GEOJIT_BLUE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.legend(fontsize=8, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    fig.tight_layout()
    return _fig_to_base64(fig)
