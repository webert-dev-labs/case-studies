"""Generate a fictitious star-schema dataset for Brightleaf Supplies.

Tables (all CSV, ready for Power BI):
- dim_date       one row per day, 2024-01-01 to 2025-12-31
- dim_branch     four invented branches
- dim_product    twelve invented products with unit price and unit cost
- fact_sales     one row per order line, with discount, net revenue and cost
- fact_inventory month-end stock per branch and product

Everything is invented and reproducible with a fixed seed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_SEED = 42
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

# (branch_id, branch_name, region, weight)
BRANCHES = [
    ("BR-01", "Harbor Point", "Coastal", 0.34),
    ("BR-02", "Cedar Hills", "Inland", 0.26),
    ("BR-03", "Maple Ridge", "Inland", 0.24),
    ("BR-04", "Silver Lake", "Coastal", 0.16),
]

# (product_name, category, unit_price, unit_cost) in USD
CATALOG = [
    ("Bamboo Desk Organizer", "Office", 24.90, 11.20),
    ("Ergo Mesh Chair", "Office", 189.00, 104.00),
    ("Graphite Notebook Set", "Office", 12.50, 4.40),
    ("Lumen LED Desk Lamp", "Lighting", 39.90, 19.50),
    ("Aurora Floor Lamp", "Lighting", 84.00, 46.20),
    ("Ceramic Pour-Over Kit", "Kitchen", 29.90, 12.10),
    ("Cast Iron Skillet", "Kitchen", 44.50, 24.90),
    ("Linen Throw Blanket", "Home Decor", 49.00, 21.50),
    ("Terracotta Plant Pot", "Home Decor", 18.75, 6.90),
    ("Woven Storage Basket", "Home Decor", 27.40, 12.30),
    ("Cordless Hand Vacuum", "Appliances", 129.00, 82.60),
    ("Smart Kettle", "Appliances", 69.90, 41.90),
]

# Relative demand by calendar month (retail seasonality: Q4 peak, quiet late winter).
MONTH_FACTOR = {1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95, 5: 1.00, 6: 1.00,
                7: 0.95, 8: 1.00, 9: 1.05, 10: 1.10, 11: 1.30, 12: 1.45}
YEAR_FACTOR = {2024: 1.00, 2025: 1.08}
# List prices rise 3% in 2025; costs stay flat, so margin improves slightly.
PRICE_FACTOR = {2024: 1.00, 2025: 1.03}
DISCOUNT_LEVELS = [0.0, 0.05, 0.10, 0.15]
DISCOUNT_WEIGHTS = [0.70, 0.15, 0.10, 0.05]

TABLES = ("dim_date", "dim_branch", "dim_product", "fact_sales", "fact_inventory")


def product_id(index: int) -> str:
    return f"PROD-{index + 1:03d}"


def dim_date(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    days = pd.date_range(start, end, freq="D")
    return pd.DataFrame({
        "date": days.strftime("%Y-%m-%d"),
        "year": days.year,
        "quarter": "Q" + days.quarter.astype(str),
        "month_number": days.month,
        "month_name": days.strftime("%b"),
        "year_month": days.strftime("%Y-%m"),
        "weekday": days.strftime("%a"),
    })


def dim_branch() -> pd.DataFrame:
    return pd.DataFrame(
        [(b, n, r) for b, n, r, _ in BRANCHES], columns=["branch_id", "branch_name", "region"]
    )


def dim_product() -> pd.DataFrame:
    return pd.DataFrame(
        [(product_id(i), n, c, p, k) for i, (n, c, p, k) in enumerate(CATALOG)],
        columns=["product_id", "product_name", "category", "unit_price", "unit_cost"],
    )


def fact_sales(dates: pd.DataFrame, base_orders_per_day: float = 9.0,
               n_customers: int = 600, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Order lines. Each order has 1-3 lines; demand follows season and yearly growth."""
    rng = np.random.default_rng(seed)
    day_index = pd.to_datetime(dates["date"])
    expected = np.array([
        base_orders_per_day * MONTH_FACTOR[d.month] * YEAR_FACTOR[d.year] for d in day_index
    ])
    orders_per_day = rng.poisson(expected)

    branch_ids = [b for b, *_ in BRANCHES]
    branch_w = [w for *_, w in BRANCHES]
    rows = []
    order_no = 0
    for day, n_orders in zip(dates["date"], orders_per_day):
        for _ in range(n_orders):
            order_no += 1
            order_id = f"ORD-{order_no:06d}"
            branch = rng.choice(branch_ids, p=branch_w)
            customer = f"CUST-{rng.integers(1, n_customers + 1):04d}"
            for _ in range(rng.integers(1, 4)):
                p = int(rng.integers(0, len(CATALOG)))
                name, _, list_price, cost = CATALOG[p]
                price = round(list_price * PRICE_FACTOR[int(day[:4])], 2)
                qty = int(rng.integers(1, 5))
                disc = float(rng.choice(DISCOUNT_LEVELS, p=DISCOUNT_WEIGHTS))
                rows.append((order_id, day, branch, customer, product_id(p), qty, price, disc,
                             round(qty * price * (1 - disc), 2), round(qty * cost, 2)))

    df = pd.DataFrame(rows, columns=[
        "order_id", "date", "branch_id", "customer_id", "product_id", "quantity",
        "unit_price", "discount_pct", "net_revenue", "cost",
    ])
    df.insert(0, "line_id", [f"LINE-{i + 1:07d}" for i in range(len(df))])
    return df


def fact_inventory(sales: pd.DataFrame, dates: pd.DataFrame, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Month-end stock per branch and product.

    Each month the branch receives roughly last month's units sold (sometimes too few),
    so stock drifts and occasionally runs out.
    """
    rng = np.random.default_rng(seed + 1)
    months = sorted(dates["year_month"].unique())
    month_end = dates.groupby("year_month")["date"].max()
    sold = (sales.assign(year_month=sales["date"].str[:7])
            .groupby(["year_month", "branch_id", "product_id"])["quantity"].sum())

    rows = []
    for branch, *_ in BRANCHES:
        for p in range(len(CATALOG)):
            pid = product_id(p)
            stock = int(rng.integers(20, 41))
            last_sold = 10
            for ym in months:
                receipts = int(round(last_sold * rng.choice([0.7, 1.0, 1.15, 1.3], p=[0.10, 0.30, 0.35, 0.25])))
                units = int(sold.get((ym, branch, pid), 0))
                stock = max(0, stock + receipts - units)
                rows.append((month_end[ym], branch, pid, stock, 5))
                last_sold = max(units, 1)

    return pd.DataFrame(rows, columns=["snapshot_date", "branch_id", "product_id",
                                       "stock_on_hand", "reorder_point"])


def generate_all(seed: int = DEFAULT_SEED) -> dict[str, pd.DataFrame]:
    dates = dim_date()
    sales = fact_sales(dates, seed=seed)
    return {
        "dim_date": dates,
        "dim_branch": dim_branch(),
        "dim_product": dim_product(),
        "fact_sales": sales,
        "fact_inventory": fact_inventory(sales, dates, seed=seed),
    }
