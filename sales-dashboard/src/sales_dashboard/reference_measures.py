"""Reference implementation of the dashboard measures.

Each function mirrors one DAX measure in powerbi/MEASURES.dax, so the numbers shown in
Power BI can be checked against docs/expected-results.md.
"""

from __future__ import annotations

import pandas as pd


def _sales_with_dims(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
    s = t["fact_sales"].merge(t["dim_branch"], on="branch_id").merge(
        t["dim_product"][["product_id", "product_name", "category"]], on="product_id")
    s["year"] = s["date"].str[:4].astype(int)
    return s


def core_measures(s: pd.DataFrame) -> dict[str, float]:
    revenue = float(s["net_revenue"].sum())
    cost = float(s["cost"].sum())
    orders = int(s["order_id"].nunique())
    gross = s["quantity"] * s["unit_price"]
    return {
        "Total Revenue": round(revenue, 2),
        "Total Cost": round(cost, 2),
        "Gross Margin": round(revenue - cost, 2),
        "Gross Margin %": round((revenue - cost) / revenue, 4) if revenue else 0.0,
        "Orders": orders,
        "Units Sold": int(s["quantity"].sum()),
        "Average Ticket": round(revenue / orders, 2) if orders else 0.0,
        "Discount Given": round(float((gross * s["discount_pct"]).sum()), 2),
    }


def by_year(t: dict[str, pd.DataFrame]) -> dict[int, dict[str, float]]:
    s = _sales_with_dims(t)
    return {int(y): core_measures(g) for y, g in s.groupby("year")}


def revenue_yoy(t: dict[str, pd.DataFrame], year: int) -> float:
    years = by_year(t)
    current, last = years[year]["Total Revenue"], years[year - 1]["Total Revenue"]
    return round((current - last) / last, 4)


def revenue_by(t: dict[str, pd.DataFrame], column: str, year: int) -> pd.Series:
    s = _sales_with_dims(t)
    return s[s["year"] == year].groupby(column)["net_revenue"].sum().round(2).sort_values(ascending=False)


def margin_pct_by(t: dict[str, pd.DataFrame], column: str, year: int) -> pd.Series:
    s = _sales_with_dims(t)
    g = s[s["year"] == year].groupby(column)[["net_revenue", "cost"]].sum()
    return ((g["net_revenue"] - g["cost"]) / g["net_revenue"]).round(4).sort_values(ascending=False)


def stock_on_hand(t: dict[str, pd.DataFrame], snapshot_date: str) -> int:
    inv = t["fact_inventory"]
    return int(inv.loc[inv["snapshot_date"] == snapshot_date, "stock_on_hand"].sum())


def stockout_rate(t: dict[str, pd.DataFrame], year: int | None = None) -> float:
    inv = t["fact_inventory"]
    if year is not None:
        inv = inv[inv["snapshot_date"].str[:4] == str(year)]
    return round(float((inv["stock_on_hand"] == 0).mean()), 4)


def days_of_supply(t: dict[str, pd.DataFrame], year: int) -> float:
    """Stock at the year's last snapshot divided by the year's average daily units sold."""
    dates = t["dim_date"]
    days = int((dates["year"] == year).sum())
    units = by_year(t)[year]["Units Sold"]
    return round(stock_on_hand(t, f"{year}-12-31") / (units / days), 1)
