# Data model

A star schema: two fact tables share three dimensions. Every relationship is
one-to-many, single direction, from the dimension (one) to the fact (many).

```
              dim_date (date)
               │          │
        1:*    │          │   1:*
               ▼          ▼
 dim_branch ─► fact_sales      fact_inventory ◄─ dim_branch
 dim_product ─►                               ◄─ dim_product
```

| From (one side) | To (many side) | Key |
|---|---|---|
| `dim_date[date]` | `fact_sales[date]` | date |
| `dim_date[date]` | `fact_inventory[snapshot_date]` | date |
| `dim_branch[branch_id]` | `fact_sales[branch_id]` | branch |
| `dim_branch[branch_id]` | `fact_inventory[branch_id]` | branch |
| `dim_product[product_id]` | `fact_sales[product_id]` | product |
| `dim_product[product_id]` | `fact_inventory[product_id]` | product |

## Tables

| Table | Grain | Rows | Notes |
|---|---|---|---|
| `dim_date` | one day | 731 | 2024-01-01 to 2025-12-31. **Mark as date table** on `date`. Sort `month_name` by `month_number`. |
| `dim_branch` | one branch | 4 | `region` groups branches into Coastal and Inland. |
| `dim_product` | one product | 12 | `unit_price` is the 2024 list price; `unit_cost` is the purchase cost. |
| `fact_sales` | one order line | 14,125 | `unit_price` already includes the 3% list-price rise in 2025. `net_revenue` = quantity × unit_price × (1 − discount_pct). |
| `fact_inventory` | month-end stock per branch and product | 1,152 | Semi-additive: add across branches and products, never across dates (use the last snapshot). |

## Data types to set in Power Query

| Column | Type |
|---|---|
| all `date` / `snapshot_date` columns | Date |
| `year`, `month_number`, `quantity`, `stock_on_hand`, `reorder_point` | Whole number |
| `unit_price`, `unit_cost`, `net_revenue`, `cost` | Fixed decimal (currency) |
| `discount_pct` | Decimal number (format as percentage) |
| every `_id` and name column | Text |

## Hide from report view

Hide the key columns on the fact tables (`date`, `branch_id`, `product_id`,
`snapshot_date`) and the raw numeric columns once measures exist, so report users
build visuals from dimensions and measures only.
