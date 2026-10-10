"""Generate fictitious sales data for Brightleaf Supplies.

All names, products and branches are invented. A fixed seed makes the
output fully reproducible.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_SEED = 42

COLUMNS = [
    "order_id",
    "order_date",
    "branch",
    "customer_id",
    "product_id",
    "product_name",
    "category",
    "quantity",
    "unit_price",
    "total",
]

BRANCHES = ["Harbor Point", "Cedar Hills", "Maple Ridge", "Silver Lake"]

# (product_name, category, unit_price in USD)
CATALOG = [
    ("Bamboo Desk Organizer", "Office", 24.90),
    ("Ergo Mesh Chair", "Office", 189.00),
    ("Graphite Notebook Set", "Office", 12.50),
    ("Lumen LED Desk Lamp", "Lighting", 39.90),
    ("Aurora Floor Lamp", "Lighting", 84.00),
    ("Ceramic Pour-Over Kit", "Kitchen", 29.90),
    ("Cast Iron Skillet", "Kitchen", 44.50),
    ("Linen Throw Blanket", "Home Decor", 49.00),
    ("Terracotta Plant Pot", "Home Decor", 18.75),
    ("Woven Storage Basket", "Home Decor", 27.40),
    ("Cordless Hand Vacuum", "Appliances", 129.00),
    ("Smart Kettle", "Appliances", 69.90),
]

# Relative popularity of each branch (sums to 1).
BRANCH_WEIGHTS = [0.35, 0.25, 0.25, 0.15]


def product_id(index: int) -> str:
    return f"PROD-{index + 1:03d}"


def customer_id(index: int) -> str:
    return f"CUST-{index + 1:04d}"


def order_id(index: int) -> str:
    return f"ORD-{index + 1:05d}"


def generate_sales(
    n_orders: int = 500,
    n_customers: int = 120,
    start_date: str = "2025-01-01",
    end_date: str = "2025-12-31",
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    """Return a DataFrame with one row per order line, sorted by date."""
    if n_orders <= 0:
        raise ValueError("n_orders must be positive")
    if n_customers <= 0:
        raise ValueError("n_customers must be positive")

    rng = np.random.default_rng(seed)
    days = pd.date_range(start_date, end_date, freq="D")
    if len(days) == 0:
        raise ValueError("end_date must not be before start_date")

    dates = rng.choice(days.to_numpy(), size=n_orders)
    branches = rng.choice(BRANCHES, size=n_orders, p=BRANCH_WEIGHTS)
    customers = rng.integers(0, n_customers, size=n_orders)
    products = rng.integers(0, len(CATALOG), size=n_orders)
    quantities = rng.integers(1, 6, size=n_orders)

    df = pd.DataFrame(
        {
            "order_date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
            "branch": branches,
            "customer_id": [customer_id(c) for c in customers],
            "product_id": [product_id(p) for p in products],
            "product_name": [CATALOG[p][0] for p in products],
            "category": [CATALOG[p][1] for p in products],
            "quantity": quantities,
            "unit_price": [CATALOG[p][2] for p in products],
        }
    )
    df = df.sort_values("order_date", kind="stable").reset_index(drop=True)
    df.insert(0, "order_id", [order_id(i) for i in range(len(df))])
    df["total"] = (df["quantity"] * df["unit_price"]).round(2)
    return df[COLUMNS]
