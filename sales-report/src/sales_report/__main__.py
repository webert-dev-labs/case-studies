"""Command-line entry point: python -m sales_report <command>."""

from __future__ import annotations

import argparse
from pathlib import Path

from sales_report.generate_data import DEFAULT_SEED, generate_sales
from sales_report.metrics import load_sales
from sales_report.report import write_report

DEFAULT_SAMPLE = Path("examples/sales-report/sales_sample.csv")
DEFAULT_REPORT = Path("output/sales-report/report.html")


def cmd_generate(args: argparse.Namespace) -> None:
    df = generate_sales(n_orders=args.orders, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} fictitious orders to {args.out}")


def cmd_report(args: argparse.Namespace) -> None:
    df = load_sales(args.data)
    path = write_report(df, args.out)
    print(f"Report for {len(df)} orders written to {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales_report",
        description="Fictitious sales data and reports for Brightleaf Supplies.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a fictitious sales CSV.")
    gen.add_argument("--orders", type=int, default=500, help="Number of orders (default: 500).")
    gen.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed (default: 42).")
    gen.add_argument("--out", type=Path, default=DEFAULT_SAMPLE, help="Output CSV path.")
    gen.set_defaults(func=cmd_generate)

    rep = sub.add_parser("report", help="Build the HTML report from a sales CSV.")
    rep.add_argument("--data", type=Path, default=DEFAULT_SAMPLE, help="Input CSV path.")
    rep.add_argument("--out", type=Path, default=DEFAULT_REPORT, help="Output HTML path.")
    rep.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
