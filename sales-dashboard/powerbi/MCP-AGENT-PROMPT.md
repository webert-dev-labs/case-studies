# Prompt for the Power BI Modeling MCP agent

Use this to let an AI agent in VS Code build the semantic model through Microsoft's
Power BI Modeling MCP server (preview). The agent builds tables, relationships and
measures, including SVG measures that draw each page as an image for native visuals (no
custom visual, no store sign-in); placing them on the canvas is a few clicks per page
(BUILD-GUIDE.md, step 4).

## Before you start

1. Install only the official extension (publisher **Microsoft**, source
   `github.com/microsoft/powerbi-modeling-mcp`).
2. Open a **new, empty** Power BI Desktop file. Do not open any other model while the
   agent is connected: it can read and change whatever model it is connected to.
3. Open the folder that contains this file in VS Code. It must also contain `MODEL.md`,
   `MEASURES.dax`, `SVG-MEASURES.dax`, `expected-results.md` and the `data/` folder with the
   five CSV files.
4. Keep tool approvals manual: approve each step after reading what it will do.
5. Put the folder outside your user profile (for example `C:\brightleaf-powerbi`), so file
   paths in the model and in the agent chat do not contain your Windows user name.
6. Never use Publish, Publish to web or Share: the report stays on this computer.

## Prompt (copy everything below the line into the agent chat)

---

Connect to the Power BI Desktop instance that has an empty model open. Build the
semantic model described in `MODEL.md` and `MEASURES.dax` in this workspace. Work in
this order and stop to report after each step.

**Step 1 — Tables.** Create five import tables named exactly `dim_date`, `dim_branch`,
`dim_product`, `fact_sales` and `fact_inventory`, each loaded from the CSV file with the
same name in the `data/` folder of this workspace. Use a Power Query (M) partition per
table: `Csv.Document` with comma delimiter and UTF-8 encoding, promote headers, then
`Table.TransformColumnTypes` with culture `"en-US"`. Column types:

- `dim_date`: date → date; year, month_number → Int64; quarter, month_name, year_month, weekday → text
- `dim_branch`: all columns → text
- `dim_product`: product_id, product_name, category → text; unit_price, unit_cost → Currency
- `fact_sales`: line_id, order_id, branch_id, customer_id, product_id → text; date → date;
  quantity → Int64; unit_price, net_revenue, cost → Currency; discount_pct → number
- `fact_inventory`: snapshot_date → date; branch_id, product_id → text;
  stock_on_hand, reorder_point → Int64

Refresh the tables and report the row count of each. Expected: 731, 4, 12, 14,125 and 1,152.

**Step 2 — Relationships.** Create the six relationships listed in `MODEL.md`: one-to-many,
single cross-filter direction, dimension on the one side. Mark `dim_date` as a date table
using `dim_date[date]`. Set `dim_date[month_name]` to sort by `dim_date[month_number]`.

**Step 3 — Measures.** Create a table named `_Measures` to hold the measures. Create every
measure in `MEASURES.dax` with exactly the same name and DAX expression, and set the format
string described in the comment above each one. Then create every measure in
`SVG-MEASURES.dax` in the same `_Measures` table, exactly as written, and set the data
category of each one to **Image URL**. Do not invent new measures.

**Step 4 — Hide columns.** Hide the key columns on the fact tables (`date`, `branch_id`,
`product_id`, `snapshot_date`) and the raw numeric columns of `fact_sales` and
`fact_inventory`.

**Step 5 — Validate.** Run DAX queries that evaluate each measure for the years 2024 and
2025, revenue by branch for 2025, gross margin % by category for 2025, and the inventory
measures listed in `expected-results.md`. Compare every value with `expected-results.md`
and show a table with expected value, actual value and match (yes/no). Do not change any
measure to force a match; if something does not match, report it and explain the likely
cause. Then evaluate each SVG measure for 2025 and confirm it returns text that starts with
`data:image/svg+xml;utf8,<svg` and contains no `#` character. If an SVG measure has a DAX
error, report the measure name and the error, propose the smallest fix, and wait for
approval before changing it.

Do not connect to any other model, do not read files outside this workspace, and do not
send data anywhere.

## Follow-up prompt: update the SVG measures after SVG-MEASURES.dax changes

---

Replace the DAX expression of each of the six measures in `SVG-MEASURES.dax` (`SVG Overview
KPIs`, `SVG Monthly Revenue`, `SVG Category Margin`, `SVG Branch Table`, `SVG Top Products`,
`SVG Inventory`) with the version in that file. Keep the names, the `_Measures` table and the
Image URL data category. Then evaluate each one for 2025 and confirm it starts with
`data:image/svg+xml;utf8,<svg`, contains `width='512'` and contains no `#`. Report any DAX error and wait
for approval before fixing it. Do not change any other measure.

## Follow-up prompt: zero instead of blank in Stockout Rate

---

Update only the measure `Stockout Rate` in the `_Measures` table to the expression in
`MEASURES.dax` (it adds `+ 0` to the stockout count). Keep its name and format string. Then
evaluate `Stockout Rate` for 2024 and 2025 (expected 5.90% and 0.69%) and evaluate it by
`dim_date[month_number]` for 2025: every month must return a number (0 where there were no
stockouts), none blank. Do not change any other measure.
