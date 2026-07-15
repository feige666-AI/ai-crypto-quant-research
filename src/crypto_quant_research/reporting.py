"""Stable CSV and JSON output helpers."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .backtest import BacktestResult
from .exceptions import OutputError
from .strategy import Signal


def _write_rows(path: str | Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    output = Path(path)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        raise OutputError(f"Cannot write CSV {output}: {exc}") from exc


def write_signals(signals: list[Signal], path: str | Path) -> None:
    """Write stable moving-average signal columns."""
    rows = [
        {
            "timestamp": signal.timestamp,
            "close": signal.close,
            "short_ma": "" if signal.short_ma is None else round(signal.short_ma, 8),
            "long_ma": "" if signal.long_ma is None else round(signal.long_ma, 8),
            "signal": signal.action,
        }
        for signal in signals
    ]
    _write_rows(path, ["timestamp", "close", "short_ma", "long_ma", "signal"], rows)


def write_equity_curve(result: BacktestResult, path: str | Path) -> None:
    """Write one row per input bar."""
    fields = [
        "timestamp",
        "close",
        "short_ma",
        "long_ma",
        "signal",
        "executed_action",
        "cash",
        "asset_qty",
        "equity",
        "benchmark_equity",
        "peak_equity",
        "drawdown_pct",
        "cumulative_fees",
    ]
    _write_rows(path, fields, result.equity_curve)


def write_trades(result: BacktestResult, path: str | Path) -> None:
    """Write completed trades; an empty run still gets a header."""
    fields = [
        "trade_id",
        "entry_timestamp",
        "entry_price",
        "exit_timestamp",
        "exit_price",
        "quantity",
        "entry_fee",
        "exit_fee",
        "gross_pnl",
        "net_pnl",
        "return_pct",
        "bars_held",
        "exit_reason",
    ]
    _write_rows(path, fields, [asdict(trade) for trade in result.trades])


def build_summary_payload(
    result: BacktestResult,
    *,
    input_file: str | Path,
    data_rows: int,
    start_timestamp: str,
    end_timestamp: str,
    short_window: int,
    long_window: int,
    fee_rate: float,
    slippage_rate: float,
    close_position_at_end: bool,
    data_type: str = "synthetic",
) -> dict[str, Any]:
    """Create the stable JSON schema used by the CLI and sample output."""
    summary = result.summary
    return {
        "project_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_type": data_type,
        "input_file": Path(input_file).as_posix(),
        "data_rows": data_rows,
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp,
        "short_window": short_window,
        "long_window": long_window,
        "initial_cash": summary.initial_cash,
        "fee_rate": fee_rate,
        "slippage_rate": slippage_rate,
        "close_position_at_end": close_position_at_end,
        "final_equity": summary.final_equity,
        "total_return_pct": summary.total_return_pct,
        "benchmark_return_pct": summary.benchmark_return_pct,
        "excess_return_pct": summary.excess_return_pct,
        "max_drawdown_pct": summary.max_drawdown_pct,
        "completed_trades": summary.completed_trades,
        "winning_trades": summary.winning_trades,
        "losing_trades": summary.losing_trades,
        "win_rate_pct": summary.win_rate_pct,
        "profit_factor": summary.profit_factor,
        "total_fees": summary.total_fees,
        "exposure_pct": summary.exposure_pct,
        "open_position": summary.open_position,
        "assumptions": [
            "Signals use the current bar close and execute at that close with slippage.",
            "The simulation is single-asset, long-only, and all-in/all-out.",
            "Fees are charged on entry and exit notional.",
            "Synthetic data and simplified execution are not evidence of live performance.",
        ],
    }


def write_summary(payload: dict[str, Any], path: str | Path) -> None:
    """Write a UTF-8 JSON summary."""
    output = Path(path)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        raise OutputError(f"Cannot write JSON {output}: {exc}") from exc
