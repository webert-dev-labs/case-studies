"""Render docs/expected-results.md: the numbers Power BI must show."""

from __future__ import annotations

import pandas as pd

from sales_dashboard import reference_measures as rm


def _usd(v: float) -> str:
    return f"${v:,.2f}"


def _pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def render(t: dict[str, pd.DataFrame]) -> str:
    years = rm.by_year(t)
    y1, y2 = sorted(years)
    keys = ["Total Revenue", "Total Cost", "Gross Margin", "Gross Margin %", "Orders",
            "Units Sold", "Average Ticket", "Discount Given"]

    def fmt(k: str, v: float) -> str:
        if k.endswith("%"):
            return _pct(v)
        if k in ("Orders", "Units Sold"):
            return f"{int(v):,}"
        return _usd(v)

    core = _table(["Measure", str(y1), str(y2)],
                  [[k, fmt(k, years[y1][k]), fmt(k, years[y2][k])] for k in keys])
    branch = _table(["Branch", f"Revenue {y2}"],
                    [[b, _usd(v)] for b, v in rm.revenue_by(t, "branch_name", y2).items()])
    category = _table(["Category", f"Gross Margin % {y2}"],
                      [[c, _pct(v)] for c, v in rm.margin_pct_by(t, "category", y2).items()])
    inventory = _table(["Measure", "Value"], [
        [f"Stock on Hand ({y2}-12-31)", f"{rm.stock_on_hand(t, f'{y2}-12-31'):,} units"],
        [f"Stockout Rate {y1}", _pct(rm.stockout_rate(t, y1))],
        [f"Stockout Rate {y2}", _pct(rm.stockout_rate(t, y2))],
        [f"Days of Supply ({y2})", f"{rm.days_of_supply(t, y2)} days"],
    ])

    return f"""# Expected results

Numbers the Power BI report must show for the sample dataset. Generated from the
reference implementation in `src/sales_dashboard/reference_measures.py`; do not edit
by hand (run `python -m sales_dashboard expected`).

Use them to check each card and visual after building the report: filter the report to
the year shown and compare. Small differences in the last decimal come from rounding
in the visual's format string, not from a wrong measure.

## Core measures by year

{core}

**Revenue YoY % ({y2}):** {_pct(rm.revenue_yoy(t, y2))}

## Revenue by branch

{branch}

## Gross margin by category

{category}

## Inventory

{inventory}
"""
