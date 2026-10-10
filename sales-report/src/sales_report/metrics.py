"""Pure functions that compute sales KPIs from an order-line DataFrame."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Summary:
    total_revenue: float
    order_count: int
    units_sold: int
    average_ticket: float
    unique_customers: int


def load_sales(path) -> pd.DataFrame:
    """Read a sales CSV and parse the order date."""
    return pd.read_csv(path, parse_dates=["order_date"])


def summary(df: pd.DataFrame) -> Summary:
    revenue = float(df["total"].sum())
    orders = int(df["order_id"].nunique())
    return Summary(
        total_revenue=round(revenue, 2),
        order_count=orders,
        units_sold=int(df["quantity"].sum()),
        average_ticket=round(revenue / orders, 2) if orders else 0.0,
        unique_customers=int(df["customer_id"].nunique()),
    )


def revenue_by_month(df: pd.DataFrame) -> pd.Series:
    """Revenue per calendar month, indexed by 'YYYY-MM' strings in order."""
    months = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m")
    return df.groupby(months)["total"].sum().round(2).sort_index().rename("revenue")


def revenue_by(df: pd.DataFrame, column: str) -> pd.Series:
    """Revenue grouped by any column, highest first."""
    return df.groupby(column)["total"].sum().round(2).sort_values(ascending=False).rename("revenue")


def top_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Top-n products by revenue with units sold."""
    grouped = df.groupby(["product_id", "product_name"], as_index=False).agg(
        units=("quantity", "sum"), revenue=("total", "sum")
    )
    grouped["revenue"] = grouped["revenue"].round(2)
    return (
        grouped.sort_values(["revenue", "product_id"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )
