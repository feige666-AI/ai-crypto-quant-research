"""Command-line entry point for the local research demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from .backtest import run_long_only_backtest, write_equity_curve, write_summary
from .data_loader import read_ohlcv_csv
from .strategy import generate_ma_signals


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-crypto-quant-research",
        description="Run a local CSV moving-average backtest demo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    backtest_parser = subparsers.add_parser("backtest", help="Run a sample long-only backtest")
    backtest_parser.add_argument("--input", required=True, help="Input OHLCV CSV file")
    backtest_parser.add_argument("--output", required=True, help="Output equity curve CSV file")
    backtest_parser.add_argument("--summary-output", help="Optional output summary JSON file")
    backtest_parser.add_argument("--short-window", type=int, default=3, help="Short moving-average window")
    backtest_parser.add_argument("--long-window", type=int, default=5, help="Long moving-average window")
    backtest_parser.add_argument("--initial-cash", type=float, default=10_000.0, help="Initial cash for demo")
    backtest_parser.add_argument("--fee-rate", type=float, default=0.001, help="Trading fee rate, e.g. 0.001")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "backtest":
        bars = read_ohlcv_csv(args.input)
        signals = generate_ma_signals(bars, short_window=args.short_window, long_window=args.long_window)
        result = run_long_only_backtest(signals, initial_cash=args.initial_cash, fee_rate=args.fee_rate)
        write_equity_curve(result, args.output)
        if args.summary_output:
            write_summary(result, args.summary_output)

        print(f"Rows: {len(result.equity_curve)}")
        print(f"Trades: {result.summary.trades}")
        print(f"Final equity: {result.summary.final_equity}")
        print(f"Return pct: {result.summary.return_pct}%")
        print(f"Output: {Path(args.output)}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
