"""Build a self-contained HTML sales report (charts embedded, no network)."""

from __future__ import annotations

import base64
import html
import io
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from sales_report import metrics  # noqa: E402

STORE_NAME = "Brightleaf Supplies"

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SERIES = "#2a78d6"

# The report is a single offline file: no scripts, no external requests, inline styles
# and embedded (data:) images only.
CSP = (
    "default-src 'none'; img-src data:; style-src 'unsafe-inline'; "
    "base-uri 'none'; form-action 'none'"
)


def usd(value: float) -> str:
    return f"${value:,.2f}"


def _usd_axis(value, _pos) -> str:
    return f"${value / 1000:,.0f}k" if abs(value) >= 1000 else f"${value:,.0f}"


def _new_axes(title: str):
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=110)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=12, color=TEXT_PRIMARY, pad=12)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9, length=0)
    ax.set_axisbelow(True)
    return fig, ax


def _to_base64(fig) -> str:
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", facecolor=fig.get_facecolor(), metadata={"Software": None})
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def monthly_chart(series: pd.Series) -> str:
    fig, ax = _new_axes("Revenue by month (USD)")
    labels = [pd.Timestamp(m + "-01").strftime("%b") for m in series.index]
    ax.bar(labels, series.values, color=SERIES, width=0.6)
    ax.yaxis.set_major_formatter(FuncFormatter(_usd_axis))
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    peak = series.idxmax()
    ax.annotate(
        usd(series[peak]),
        xy=(list(series.index).index(peak), series[peak]),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        fontsize=8,
        color=TEXT_PRIMARY,
    )
    return _to_base64(fig)


def horizontal_chart(series: pd.Series, title: str) -> str:
    ordered = series.sort_values()
    fig, ax = _new_axes(title)
    ax.barh(ordered.index, ordered.values, color=SERIES, height=0.55)
    ax.xaxis.set_major_formatter(FuncFormatter(_usd_axis))
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    for y, value in enumerate(ordered.values):
        ax.text(value, y, f" {usd(value)}", va="center", fontsize=8, color=TEXT_PRIMARY)
    ax.margins(x=0.18)
    return _to_base64(fig)


def _table(headers: list[str], rows: list[list[str]], numeric_from: int = 1) -> str:
    head = "".join(
        f'<th class="{"num" if i >= numeric_from else ""}">{html.escape(h)}</th>'
        for i, h in enumerate(headers)
    )
    body = "".join(
        "<tr>"
        + "".join(
            f'<td class="{"num" if i >= numeric_from else ""}">{html.escape(str(c))}</td>'
            for i, c in enumerate(row)
        )
        + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _figure(image: str, alt: str) -> str:
    return f'<img src="data:image/png;base64,{image}" alt="{html.escape(alt)}">'


def build_html(df: pd.DataFrame, generated_on: date | None = None) -> str:
    generated_on = generated_on or date.today()
    s = metrics.summary(df)
    by_month = metrics.revenue_by_month(df)
    by_branch = metrics.revenue_by(df, "branch")
    by_category = metrics.revenue_by(df, "category")
    top = metrics.top_products(df, n=5)

    dates = pd.to_datetime(df["order_date"])
    period = f"{dates.min():%Y-%m-%d} to {dates.max():%Y-%m-%d}"

    kpis = [
        ("Total revenue", usd(s.total_revenue)),
        ("Orders", f"{s.order_count:,}"),
        ("Average ticket", usd(s.average_ticket)),
        ("Units sold", f"{s.units_sold:,}"),
        ("Customers", f"{s.unique_customers:,}"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div></div>'
        for label, value in kpis
    )

    month_table = _table(
        ["Month", "Revenue"], [[m, usd(v)] for m, v in by_month.items()]
    )
    branch_table = _table(
        ["Branch", "Revenue", "Share"],
        [[b, usd(v), f"{v / s.total_revenue:.1%}"] for b, v in by_branch.items()],
    )
    category_table = _table(
        ["Category", "Revenue", "Share"],
        [[c, usd(v), f"{v / s.total_revenue:.1%}"] for c, v in by_category.items()],
    )
    top_table = _table(
        ["#", "Product ID", "Product", "Units", "Revenue"],
        [
            [i + 1, r.product_id, r.product_name, f"{r.units:,}", usd(r.revenue)]
            for i, r in enumerate(top.itertuples())
        ],
        numeric_from=3,
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="no-referrer">
<title>{STORE_NAME} Sales Report</title>
<style>
  :root {{
    --surface: {SURFACE}; --card: #ffffff; --text: {TEXT_PRIMARY};
    --muted: {TEXT_SECONDARY}; --line: {GRID};
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--surface); color: var(--text);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; line-height: 1.5; }}
  main {{ max-width: 960px; margin: 0 auto; padding: 32px 16px 48px; }}
  h1 {{ margin: 0; font-size: 1.6rem; }}
  h2 {{ font-size: 1.1rem; margin: 0 0 12px; }}
  .meta {{ color: var(--muted); margin: 4px 0 24px; font-size: .9rem; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px; margin-bottom: 24px; }}
  .kpi, section {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; }}
  .kpi {{ padding: 14px 16px; }}
  .kpi .label {{ color: var(--muted); font-size: .8rem; }}
  .kpi .value {{ font-size: 1.35rem; font-weight: 600; font-variant-numeric: tabular-nums; }}
  section {{ padding: 20px; margin-bottom: 20px; }}
  img {{ width: 100%; height: auto; display: block; }}
  details {{ margin-top: 8px; }}
  summary {{ cursor: pointer; color: var(--muted); font-size: .85rem; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .9rem; margin-top: 8px; }}
  th, td {{ padding: 6px 8px; border-bottom: 1px solid var(--line); text-align: left; }}
  th {{ color: var(--muted); font-weight: 600; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  footer {{ color: var(--muted); font-size: .8rem; text-align: center; }}
</style>
</head>
<body>
<main>
  <h1>{STORE_NAME} &mdash; Sales Report</h1>
  <p class="meta">Period: {period} &middot; Generated on {generated_on:%Y-%m-%d} &middot; All values in USD</p>
  <div class="kpis">{kpi_html}</div>

  <section>
    {_figure(monthly_chart(by_month), "Bar chart of revenue by month")}
    <details><summary>Show data table</summary><div class="table-wrap">{month_table}</div></details>
  </section>

  <section>
    {_figure(horizontal_chart(by_branch, "Revenue by branch (USD)"), "Bar chart of revenue by branch")}
    <details><summary>Show data table</summary><div class="table-wrap">{branch_table}</div></details>
  </section>

  <section>
    {_figure(horizontal_chart(by_category, "Revenue by category (USD)"), "Bar chart of revenue by category")}
    <details><summary>Show data table</summary><div class="table-wrap">{category_table}</div></details>
  </section>

  <section>
    <h2>Top 5 products by revenue</h2>
    <div class="table-wrap">{top_table}</div>
  </section>

  <footer>Fictitious data for demonstration purposes only.</footer>
</main>
</body>
</html>
"""


def write_report(df: pd.DataFrame, out_path: Path, generated_on: date | None = None) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_html(df, generated_on), encoding="utf-8")
    return out_path
