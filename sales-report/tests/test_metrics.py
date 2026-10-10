import pandas as pd
import pytest

from sales_report.metrics import (
    load_sales,
    revenue_by,
    revenue_by_month,
    summary,
    top_products,
)


@pytest.fixture
def sales():
    return pd.DataFrame(
        {
            "order_id": ["ORD-00001", "ORD-00002", "ORD-00003", "ORD-00004"],
            "order_date": pd.to_datetime(["2025-01-10", "2025-01-20", "2025-02-05", "2025-02-28"]),
            "branch": ["Cedar Hills", "Maple Ridge", "Cedar Hills", "Cedar Hills"],
            "customer_id": ["CUST-0001", "CUST-0002", "CUST-0001", "CUST-0003"],
            "product_id": ["PROD-001", "PROD-002", "PROD-001", "PROD-003"],
            "product_name": ["Desk", "Lamp", "Desk", "Pot"],
            "category": ["Office", "Lighting", "Office", "Home Decor"],
            "quantity": [2, 1, 1, 4],
            "unit_price": [50.0, 30.0, 50.0, 5.0],
            "total": [100.0, 30.0, 50.0, 20.0],
        }
    )


def test_summary(sales):
    s = summary(sales)
    assert s.total_revenue == 200.0
    assert s.order_count == 4
    assert s.units_sold == 8
    assert s.average_ticket == 50.0
    assert s.unique_customers == 3


def test_summary_of_empty_data(sales):
    s = summary(sales.iloc[0:0])
    assert s.total_revenue == 0.0
    assert s.average_ticket == 0.0


def test_revenue_by_month(sales):
    result = revenue_by_month(sales)
    assert result.to_dict() == {"2025-01": 130.0, "2025-02": 70.0}


def test_revenue_by_branch_sorted_desc(sales):
    result = revenue_by(sales, "branch")
    assert list(result.index) == ["Cedar Hills", "Maple Ridge"]
    assert list(result) == [170.0, 30.0]


def test_top_products(sales):
    result = top_products(sales, n=2)
    assert list(result["product_name"]) == ["Desk", "Lamp"]
    assert list(result["units"]) == [3, 1]
    assert list(result["revenue"]) == [150.0, 30.0]


def test_load_sales_parses_dates(tmp_path, sales):
    path = tmp_path / "sales.csv"
    sales.to_csv(path, index=False)
    loaded = load_sales(path)
    assert pd.api.types.is_datetime64_any_dtype(loaded["order_date"])
    assert summary(loaded) == summary(sales)
