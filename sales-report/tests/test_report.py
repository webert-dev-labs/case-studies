from datetime import date

from sales_report.__main__ import main
from sales_report.generate_data import generate_sales
from sales_report.metrics import summary
from sales_report.report import build_html, usd, write_report


def test_usd_format():
    assert usd(1234.5) == "$1,234.50"
    assert usd(0) == "$0.00"


def test_html_contains_kpis_and_charts():
    df = generate_sales(n_orders=80)
    page = build_html(df, generated_on=date(2026, 1, 15))
    s = summary(df)
    assert "Brightleaf Supplies" in page
    assert usd(s.total_revenue) in page
    assert usd(s.average_ticket) in page
    assert "Generated on 2026-01-15" in page
    assert page.count('<img src="data:image/png;base64,') == 3
    assert "http://" not in page and "https://" not in page


def test_html_has_security_headers():
    page = build_html(generate_sales(n_orders=20), generated_on=date(2026, 1, 15))
    assert "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none';" in page
    assert '<meta name="referrer" content="no-referrer">' in page
    assert "<script" not in page


def test_chart_images_carry_no_software_metadata():
    page = build_html(generate_sales(n_orders=20), generated_on=date(2026, 1, 15))
    first = page.split('data:image/png;base64,')[1].split('"')[0]
    import base64
    assert b"Software" not in base64.b64decode(first)


def test_write_report_creates_file(tmp_path):
    out = write_report(generate_sales(n_orders=30), tmp_path / "nested" / "report.html")
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_cli_generate_then_report(tmp_path, capsys):
    csv_path = tmp_path / "sales.csv"
    html_path = tmp_path / "report.html"
    main(["generate", "--orders", "40", "--out", str(csv_path)])
    main(["report", "--data", str(csv_path), "--out", str(html_path)])
    assert html_path.exists()
    assert "Report for 40 orders" in capsys.readouterr().out
