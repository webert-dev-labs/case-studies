import re

import pandas as pd
import pytest

from sales_report.generate_data import BRANCHES, CATALOG, COLUMNS, generate_sales


def test_same_seed_gives_identical_data():
    first = generate_sales(n_orders=200, seed=7)
    second = generate_sales(n_orders=200, seed=7)
    pd.testing.assert_frame_equal(first, second)


def test_different_seed_gives_different_data():
    assert not generate_sales(n_orders=200, seed=1).equals(generate_sales(n_orders=200, seed=2))


def test_schema_and_row_count():
    df = generate_sales(n_orders=50)
    assert list(df.columns) == COLUMNS
    assert len(df) == 50


def test_ids_use_neutral_formats():
    df = generate_sales(n_orders=100)
    assert df["order_id"].str.fullmatch(r"ORD-\d{5}").all()
    assert df["customer_id"].str.fullmatch(r"CUST-\d{4}").all()
    assert df["product_id"].str.fullmatch(r"PROD-\d{3}").all()
    assert df["order_id"].is_unique


def test_values_are_valid():
    df = generate_sales(n_orders=300, start_date="2025-03-01", end_date="2025-03-31")
    assert (df["quantity"] >= 1).all()
    assert (df["unit_price"] > 0).all()
    assert ((df["quantity"] * df["unit_price"]).round(2) == df["total"]).all()
    assert set(df["branch"]) <= set(BRANCHES)
    assert set(df["product_name"]) <= {name for name, _, _ in CATALOG}
    assert df["order_date"].min() >= "2025-03-01"
    assert df["order_date"].max() <= "2025-03-31"
    assert df["order_date"].is_monotonic_increasing
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) for d in df["order_date"])


@pytest.mark.parametrize("kwargs", [{"n_orders": 0}, {"n_customers": 0}])
def test_invalid_sizes_raise(kwargs):
    with pytest.raises(ValueError):
        generate_sales(**kwargs)
