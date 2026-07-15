"""Argparse command-line interface for the local research demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

from .backtest import BacktestResult, run_long_only_backtest
from .data_loader import ValidationResult, validate_ohlcv_csv
from .exceptions import ResearchError
from .reporting import (
    build_summary_payload,
    write_equity_curve,
    write_signals,
    write_summary,
    write_trades,
)
from .strategy import Signal, generate_ma_signals
from .visualization import generate_charts


def _add_strategy_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", type=Path, required=True, help="Input OHLCV CSV file")
    parser.add_argument("--short-window", type=int, default=5, help="Short MA window (default: 5)")
    parser.add_argument("--long-window", type=int, default=20, help="Long MA window (default: 20)")


def _add_backtest_arguments(parser: argparse.ArgumentParser) -> None:
    _add_strategy_arguments(parser)
    parser.add_argument("--initial-cash", type=float, default=10_000.0, help="Initial cash")
    parser.add_argument("--fee-rate", type=float, default=0.001, help="Fee rate (default: 0.001)")
    parser.add_argument(
        "--slippage-rate", type=float, default=0.0005, help="Slippage rate (default: 0.0005)"
    )
    parser.add_argument(
        "--close-position-at-end",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Force-close an open position on the final bar (default: true)",
    )
    parser.add_argument("--equity-output", type=Path, required=True, help="Equity curve CSV")
    parser.add_argument("--trades-output", type=Path, required=True, help="Completed trades CSV")
    parser.add_argument("--summary-output", type=Path, required=True, help="Summary JSON")


def build_parser() -> argparse.ArgumentParser:
    """Build the public CLI parser."""
    parser = argparse.ArgumentParser(
        prog="crypto-quant",
        description="Validate synthetic OHLCV data and run a local moving-average research demo.",
    )
    parser.add_argument("--debug", action="store_true", help="Show tracebacks for debugging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate an OHLCV CSV file")
    validate_parser.add_argument("--input", type=Path, required=True, help="Input OHLCV CSV file")

    signals_parser = subparsers.add_parser("signals", help="Generate moving-average signals")
    _add_strategy_arguments(signals_parser)
    signals_parser.add_argument("--output", type=Path, required=True, help="Signal CSV output")

    backtest_parser = subparsers.add_parser("backtest", help="Run the long-only teaching backtest")
    _add_backtest_arguments(backtest_parser)

    subparsers.add_parser(
        "demo",
        help="Run validation, signals, backtest, reports, and charts with repository defaults",
    )
    return parser


def _print_validation(validation: ValidationResult) -> None:
    summary = validation.summary
    print("Validation status: valid")
    print(f"Input file: {summary.input_file}")
    print(f"Rows: {summary.rows}")
    print(f"Start timestamp: {summary.start_timestamp}")
    print(f"End timestamp: {summary.end_timestamp}")
    print(f"Duplicate timestamps: {summary.has_duplicate_timestamps}")
    print(f"Timestamps ascending: {summary.timestamps_ascending}")
    print(f"Columns valid: {summary.columns_valid}")
    print(f"Numeric values valid: {summary.numeric_values_valid}")
    print(f"OHLC relations valid: {summary.ohlc_relations_valid}")


def _run_backtest(
    args: argparse.Namespace | SimpleNamespace,
) -> tuple[list[Signal], BacktestResult]:
    validation = validate_ohlcv_csv(args.input)
    signals = generate_ma_signals(
        validation.bars, short_window=args.short_window, long_window=args.long_window
    )
    result = run_long_only_backtest(
        signals,
        initial_cash=args.initial_cash,
        fee_rate=args.fee_rate,
        slippage_rate=args.slippage_rate,
        close_position_at_end=args.close_position_at_end,
    )
    write_equity_curve(result, args.equity_output)
    write_trades(result, args.trades_output)
    payload = build_summary_payload(
        result,
        input_file=args.input,
        data_rows=validation.summary.rows,
        start_timestamp=validation.summary.start_timestamp,
        end_timestamp=validation.summary.end_timestamp,
        short_window=args.short_window,
        long_window=args.long_window,
        fee_rate=args.fee_rate,
        slippage_rate=args.slippage_rate,
        close_position_at_end=args.close_position_at_end,
    )
    write_summary(payload, args.summary_output)
    return signals, result


def _print_backtest(result: BacktestResult) -> None:
    summary = result.summary
    print(f"Final equity: {summary.final_equity:.2f}")
    print(f"Total return: {summary.total_return_pct:.2f}%")
    print(f"Benchmark return: {summary.benchmark_return_pct:.2f}%")
    print(f"Max drawdown: {summary.max_drawdown_pct:.2f}%")
    print(f"Completed trades: {summary.completed_trades}")
    print(f"Open position: {summary.open_position}")


def _dispatch(args: argparse.Namespace) -> int:
    if args.command == "validate":
        _print_validation(validate_ohlcv_csv(args.input))
        return 0
    if args.command == "signals":
        validation = validate_ohlcv_csv(args.input)
        signals = generate_ma_signals(
            validation.bars, short_window=args.short_window, long_window=args.long_window
        )
        write_signals(signals, args.output)
        print(f"Signals written: {len(signals)} rows -> {args.output}")
        return 0
    if args.command == "backtest":
        _, result = _run_backtest(args)
        _print_backtest(result)
        return 0
    if args.command == "demo":
        demo = SimpleNamespace(
            input=Path("data/sample_data.csv"),
            short_window=5,
            long_window=20,
            initial_cash=10_000.0,
            fee_rate=0.001,
            slippage_rate=0.0005,
            close_position_at_end=True,
            equity_output=Path("results/equity_curve_sample.csv"),
            trades_output=Path("results/trades_sample.csv"),
            summary_output=Path("results/backtest_summary_sample.json"),
        )
        validation = validate_ohlcv_csv(demo.input)
        _print_validation(validation)
        signals, result = _run_backtest(demo)
        write_signals(signals, Path("results/signals_sample.csv"))
        charts = generate_charts(signals, result, Path("docs/assets"))
        _print_backtest(result)
        print("Generated reports: results/*.csv and results/backtest_summary_sample.json")
        print(f"Generated charts: {', '.join(str(path) for path in charts)}")
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run one command, and keep expected errors concise."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except (ResearchError, OSError) as exc:
        if args.debug:
            raise
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
