from pathlib import Path

import pandas as pd
import pytest

from sales_dashboard import reference_measures as rm
from sales_dashboard.__main__ import main
from sales_dashboard.expected_results import render
from sales_dashboard.generate_data import generate_all

PROJECT = Path(__file__).resolve().parents[1]


@pytest.fixture
def tiny():
    """Hand-made tables with known answers."""
    return {
        "dim_date": pd.DataFrame({"date": ["2024-12-31", "2025-12-31"], "year": [2024, 2025]}),
        "dim_branch": pd.DataFrame({"branch_id": ["BR-01", "BR-02"], "branch_name": ["North", "South"],
                                    "region": ["A", "B"]}),
        "dim_product": pd.DataFrame({"product_id": ["PROD-001", "PROD-002"], "product_name": ["Lamp", "Pot"],
                                     "category": ["Lighting", "Decor"], "unit_price": [10.0, 5.0],
                                     "unit_cost": [6.0, 2.0]}),
        "fact_sales": pd.DataFrame({
            "line_id": ["L1", "L2", "L3", "L4"],
            "order_id": ["O1", "O1", "O2", "O3"],
            "date": ["2024-12-31", "2024-12-31", "2025-12-31", "2025-12-31"],
            "branch_id": ["BR-01", "BR-01", "BR-02", "BR-01"],
            "customer_id": ["C1", "C1", "C2", "C3"],
            "product_id": ["PROD-001", "PROD-002", "PROD-001", "PROD-002"],
            "quantity": [2, 4, 3, 2],
            "unit_price": [10.0, 5.0, 10.0, 5.0],
            "discount_pct": [0.0, 0.10, 0.0, 0.0],
            "net_revenue": [20.0, 18.0, 30.0, 10.0],
            "cost": [12.0, 8.0, 18.0, 4.0],
        }),
        "fact_inventory": pd.DataFrame({
            "snapshot_date": ["2024-12-31", "2024-12-31", "2025-12-31", "2025-12-31"],
            "branch_id": ["BR-01", "BR-02", "BR-01", "BR-02"],
            "product_id": ["PROD-001", "PROD-001", "PROD-001", "PROD-001"],
            "stock_on_hand": [0, 6, 5, 4],
            "reorder_point": [5, 5, 5, 5],
        }),
    }


def test_core_measures_on_known_data(tiny):
    y = rm.by_year(tiny)
    assert y[2024]["Total Revenue"] == 38.0
    assert y[2024]["Gross Margin"] == 18.0
    assert y[2024]["Gross Margin %"] == round(18 / 38, 4)
    assert y[2024]["Orders"] == 1
    assert y[2024]["Average Ticket"] == 38.0
    assert y[2024]["Discount Given"] == 2.0
    assert y[2025]["Orders"] == 2 and y[2025]["Units Sold"] == 5


def test_yoy_and_breakdowns(tiny):
    assert rm.revenue_yoy(tiny, 2025) == round((40 - 38) / 38, 4)
    assert rm.revenue_by(tiny, "branch_name", 2025).to_dict() == {"South": 30.0, "North": 10.0}
    assert rm.margin_pct_by(tiny, "category", 2025).to_dict() == {"Decor": 0.6, "Lighting": 0.4}


def test_inventory_measures(tiny):
    assert rm.stock_on_hand(tiny, "2025-12-31") == 9
    assert rm.stockout_rate(tiny, 2024) == 0.5
    assert rm.stockout_rate(tiny) == 0.25
    # 9 units in stock / (5 units sold over 1 day in the date table)
    assert rm.days_of_supply(tiny, 2025) == 1.8


def test_expected_results_file_is_up_to_date():
    committed = (PROJECT / "docs" / "expected-results.md").read_text(encoding="utf-8")
    assert committed == render(generate_all()), "run `python -m sales_dashboard expected`"


def test_cli_writes_all_tables(tmp_path):
    main(["generate", "--out", str(tmp_path)])
    names = sorted(p.name for p in tmp_path.glob("*.csv"))
    assert names == ["dim_branch.csv", "dim_date.csv", "dim_product.csv", "fact_inventory.csv", "fact_sales.csv"]
