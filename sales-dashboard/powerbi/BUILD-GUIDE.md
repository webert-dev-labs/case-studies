# Build guide (Power BI Desktop)

Step-by-step instructions to build the report from the CSV files. About 60–90 minutes.
No `.pbix` file is committed: the repository blocks it on purpose, because a `.pbix` can
carry hidden data and metadata. The model, measures and screenshots document the work.

> **Shortcut:** steps 1–3 (data, model and measures) can be done by an AI agent through
> Microsoft's Power BI Modeling MCP server. See [MCP-AGENT-PROMPT.md](MCP-AGENT-PROMPT.md).
> Step 4 (report pages) is always built by hand.

## 1. Load the data

1. **Get data → Text/CSV** and load the five files from `examples/sales-dashboard/`.
   For each file choose **Transform Data** instead of Load.
2. In Power Query, set the column types listed in [MODEL.md](MODEL.md#data-types-to-set-in-power-query).
   Pay attention to dates: if your Windows region is not English, use
   **Change Type → Using Locale → Date → English (United States)** so `2025-12-31` is read correctly.
3. **Close & Apply**.

## 2. Build the model

1. **Model view**: delete any relationship Power BI guessed, then create the six
   relationships from [MODEL.md](MODEL.md) (one-to-many, single cross-filter direction).
2. Select `dim_date` → **Table tools → Mark as date table** → column `date`.
3. In `dim_date`, select `month_name` → **Sort by column → month_number**.
4. Hide the key columns listed in MODEL.md.

## 3. Create the measures

1. **Home → Enter data**, name the table `_Measures`, **Load**. Delete its default column later.
2. Create each measure from [MEASURES.dax](MEASURES.dax) with **New measure** and set the
   format string written above it.

## 4. Build three pages

**Fast option — SVG measures (native visuals only, nothing to install).** On each page add
a year slicer (`dim_date[year]`, dropdown, single select, 2025). For each measure in
[SVG-MEASURES.dax](SVG-MEASURES.dax) add a native **Table** visual with only that measure in
**Columns**, then in **Format visual**: set **Image size** to the width and height noted above
the measure, and turn off column headers, totals and grid lines. The Table visual caps images
at 512 × 512 px, which is why every drawing is 512 px wide; the native Image visual cannot
read a measure.

| Page | Left column (x ≈ 40) | Right column (x ≈ 700) |
|---|---|---|
| Overview | `SVG Overview KPIs` (512 × 236), below it `SVG Category Margin` (512 × 190) | `SVG Monthly Revenue` (512 × 260) |
| Branch & product | `SVG Branch Table` (512 × 208) | `SVG Top Products` (512 × 266) |
| Inventory | `SVG Inventory` (512 × 330) | — |

Add a `dim_branch[branch_name]` slicer on the Branch & product page to drill into one branch.

**Standard option — native visuals.** Use a 16:9 page. Keep one accent color for the current year and a neutral grey for last year.

**Page 1 — Overview**
- Slicer: `dim_date[year]` (single select, default 2025).
- Cards: Total Revenue, Gross Margin %, Orders, Average Ticket, Revenue YoY %.
- Line chart: `dim_date[month_name]` on the axis; Total Revenue and Revenue LY as lines.
- Bar chart: Gross Margin % by `dim_product[category]`, sorted descending.

**Page 2 — Branch & product drill-down**
- Matrix: rows `dim_branch[region]` → `dim_branch[branch_name]` → `dim_product[category]`
  → `dim_product[product_name]`; values Total Revenue, Gross Margin, Gross Margin %, Units Sold.
  Turn on **drill-down** so a viewer can expand a branch to its categories and products.
- Bar chart: Total Revenue by `dim_branch[branch_name]`.

**Page 3 — Inventory**
- Cards: Stock on Hand, Days of Supply, Stockout Rate.
- Column chart: Stockout Rate by `dim_date[year_month]` (shows the drop in 2025).
- Table: product, branch, Stock on Hand, sorted ascending (lowest stock first).

## 5. Check the numbers

Filter each page to the year shown in [../docs/expected-results.md](../docs/expected-results.md)
and compare every card and total. They must match. If one does not, check the data types
and the relationships first.

## 6. Screenshots for the portfolio

Export at full size (**File → Export → Export to PDF** is not needed; use a screenshot tool)
and save as PNG in `sales-dashboard/docs/public/`:

| File | Content |
|---|---|
| `overview.png` | Page 1 with 2025 selected |
| `drilldown.png` | Page 2 with one branch expanded to products |
| `inventory.png` | Page 3 |
| `model.png` | Model view showing the star schema |

Before committing, open each image and check that nothing personal appears (window
titles, file paths, user names, taskbar). Crop to the report canvas.
