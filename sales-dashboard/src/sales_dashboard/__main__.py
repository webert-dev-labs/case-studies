"""Command-line entry point: python -m sales_dashboard <command>."""

from __future__ import annotations

import argparse
from pathlib import Path

from sales_dashboard.expected_results import render
from sales_dashboard.generate_data import DEFAULT_SEED, TABLES, generate_all

DEFAULT_DATA_DIR = Path("examples/sales-dashboard")
DEFAULT_EXPECTED = Path("sales-dashboard/docs/expected-results.md")


def cmd_generate(args: argparse.Namespace) -> None:
    tables = generate_all(seed=args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        tables[name].to_csv(args.out / f"{name}.csv", index=False)
        print(f"Wrote {len(tables[name]):>6,} rows to {args.out / (name + '.csv')}")


def cmd_expected(args: argparse.Namespace) -> None:
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(generate_all(seed=args.seed)), encoding="utf-8")
    print(f"Wrote expected results to {args.out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales_dashboard",
        description="Fictitious star-schema data and reference results for the Brightleaf Power BI dashboard.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Write the five CSV tables.")
    gen.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed (default: 42).")
    gen.add_argument("--out", type=Path, default=DEFAULT_DATA_DIR, help="Output folder.")
    gen.set_defaults(func=cmd_generate)

    exp = sub.add_parser("expected", help="Write the expected-results Markdown file.")
    exp.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed (default: 42).")
    exp.add_argument("--out", type=Path, default=DEFAULT_EXPECTED, help="Output Markdown path.")
    exp.set_defaults(func=cmd_expected)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
