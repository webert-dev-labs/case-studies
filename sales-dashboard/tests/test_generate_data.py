import pandas as pd
import pytest

from sales_dashboard.generate_data import CATALOG, TABLES, generate_all


@pytest.fixture(scope="module")
def tables():
    return generate_all()


def test_same_seed_gives_identical_tables():
    a, b = generate_all(seed=7), generate_all(seed=7)
    for name in TABLES:
        pd.testing.assert_frame_equal(a[name], b[name])


def test_date_table_is_continuous_and_unique(tables):
    d = pd.to_datetime(tables["dim_date"]["date"])
    assert d.is_unique and d.is_monotonic_increasing
    assert (d.diff().dropna().dt.days == 1).all()
    assert d.min() == pd.Timestamp("2024-01-01") and d.max() == pd.Timestamp("2025-12-31")


def test_dimension_keys_are_unique(tables):
    assert tables["dim_branch"]["branch_id"].is_unique
    assert tables["dim_product"]["product_id"].is_unique
    assert len(tables["dim_product"]) == len(CATALOG)


def test_fact_keys_exist_in_dimensions(tables):
    s, inv = tables["fact_sales"], tables["fact_inventory"]
    assert set(s["date"]) <= set(tables["dim_date"]["date"])
    assert set(s["branch_id"]) <= set(tables["dim_branch"]["branch_id"])
    assert set(s["product_id"]) <= set(tables["dim_product"]["product_id"])
    assert set(inv["snapshot_date"]) <= set(tables["dim_date"]["date"])
    assert set(inv["product_id"]) <= set(tables["dim_product"]["product_id"])


def test_sales_values_are_consistent(tables):
    s = tables["fact_sales"]
    assert s["line_id"].is_unique
    assert (s["quantity"] >= 1).all()
    assert s["discount_pct"].between(0, 0.15).all()
    expected = (s["quantity"] * s["unit_price"] * (1 - s["discount_pct"])).round(2)
    assert (expected - s["net_revenue"]).abs().max() < 0.011
    assert (s["cost"] > 0).all() and (s["cost"] < s["quantity"] * s["unit_price"]).all()


def test_ids_use_neutral_formats(tables):
    s = tables["fact_sales"]
    assert s["order_id"].str.fullmatch(r"ORD-\d{6}").all()
    assert s["customer_id"].str.fullmatch(r"CUST-\d{4}").all()
    assert s["product_id"].str.fullmatch(r"PROD-\d{3}").all()
    assert tables["dim_branch"]["branch_id"].str.fullmatch(r"BR-\d{2}").all()


def test_inventory_is_one_row_per_month_branch_product(tables):
    inv = tables["fact_inventory"]
    assert not inv.duplicated(["snapshot_date", "branch_id", "product_id"]).any()
    assert len(inv) == 24 * len(tables["dim_branch"]) * len(tables["dim_product"])
    assert (inv["stock_on_hand"] >= 0).all()
