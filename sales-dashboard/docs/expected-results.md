# Expected results

Numbers the Power BI report must show for the sample dataset. Generated from the
reference implementation in `src/sales_dashboard/reference_measures.py`; do not edit
by hand (run `python -m sales_dashboard expected`).

Use them to check each card and visual after building the report: filter the report to
the year shown and compare. Small differences in the last decimal come from rounding
in the visual's format string, not from a wrong measure.

## Core measures by year

| Measure | 2024 | 2025 |
|---|---|---|
| Total Revenue | $986,180.19 | $1,113,820.32 |
| Total Cost | $544,208.10 | $598,583.80 |
| Gross Margin | $441,972.09 | $515,236.52 |
| Gross Margin % | 44.82% | 46.26% |
| Orders | 3,433 | 3,642 |
| Units Sold | 17,207 | 18,251 |
| Average Ticket | $287.26 | $305.83 |
| Discount Given | $25,396.47 | $28,661.88 |

**Revenue YoY % (2025):** 12.94%

## Revenue by branch

| Branch | Revenue 2025 |
|---|---|
| Harbor Point | $378,949.18 |
| Maple Ridge | $282,826.01 |
| Cedar Hills | $273,909.24 |
| Silver Lake | $178,135.89 |

## Gross margin by category

| Category | Gross Margin % 2025 |
|---|---|
| Home Decor | 57.44% |
| Kitchen | 50.54% |
| Office | 47.41% |
| Lighting | 47.03% |
| Appliances | 37.44% |

## Inventory

| Measure | Value |
|---|---|
| Stock on Hand (2025-12-31) | 3,105 units |
| Stockout Rate 2024 | 5.90% |
| Stockout Rate 2025 | 0.69% |
| Days of Supply (2025) | 62.1 days |
