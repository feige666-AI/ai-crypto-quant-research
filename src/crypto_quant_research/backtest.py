"""Minimal long-only backtest engine for local CSV examples."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .strategy import Signal


@dataclass(frozen=True)
class BacktestSummary:
    initial_cash: float
    final_equity: float
    return_pct: float
    max_drawdown_pct: float
    trades: int


@dataclass(frozen=True)
class BacktestResult:
    summary: BacktestSummary
    equity_curve: list[dict[str, float | str]]


def run_long_only_backtest(
    signals: list[Signal],
    initial_cash: float = 10_000.0,
    fee_rate: float = 0.001,
) -> BacktestResult:
    """Run a simple all-in/all-out backtest from generated trading signals."""
    if initial_cash <= 0:
        raise ValueError("Initial cash must be greater than 0")
    if fee_rate < 0:
        raise ValueError("Fee rate cannot be negative")

    cash = initial_cash
    asset_qty = 0.0
    trades = 0
    peak_equity = initial_cash
    max_drawdown_pct = 0.0
    equity_curve: list[dict[str, float | str]] = []

    for signal in signals:
        executed_action = "hold"
        price = signal.close

        if signal.action == "buy" and asset_qty == 0 and cash > 0:
            asset_qty = (cash * (1 - fee_rate)) / price
            cash = 0.0
            trades += 1
            executed_action = "buy"
        elif signal.action == "sell" and asset_qty > 0:
            cash = asset_qty * price * (1 - fee_rate)
            asset_qty = 0.0
            trades += 1
            executed_action = "sell"

        equity = cash + asset_qty * price
        peak_equity = max(peak_equity, equity)
        drawdown_pct = ((peak_equity - equity) / peak_equity) * 100 if peak_equity else 0.0
        max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)

        equity_curve.append(
            {
                "timestamp": signal.timestamp,
                "close": round(price, 6),
                "short_ma": "" if signal.short_ma is None else round(signal.short_ma, 6),
                "long_ma": "" if signal.long_ma is None else round(signal.long_ma, 6),
                "signal": signal.action,
                "executed_action": executed_action,
                "cash": round(cash, 6),
                "asset_qty": round(asset_qty, 8),
                "equity": round(equity, 6),
                "drawdown_pct": round(drawdown_pct, 4),
            }
        )

    final_equity = float(equity_curve[-1]["equity"]) if equity_curve else initial_cash
    summary = BacktestSummary(
        initial_cash=round(initial_cash, 6),
        final_equity=round(final_equity, 6),
        return_pct=round(((final_equity - initial_cash) / initial_cash) * 100, 4),
        max_drawdown_pct=round(max_drawdown_pct, 4),
        trades=trades,
    )
    return BacktestResult(summary=summary, equity_curve=equity_curve)


def write_equity_curve(result: BacktestResult, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "timestamp",
        "close",
        "short_ma",
        "long_ma",
        "signal",
        "executed_action",
        "cash",
        "asset_qty",
        "equity",
        "drawdown_pct",
    ]
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result.equity_curve)


def write_summary(result: BacktestResult, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result.summary), ensure_ascii=False, indent=2), encoding="utf-8")
