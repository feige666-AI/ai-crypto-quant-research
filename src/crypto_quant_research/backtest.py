"""Deterministic, single-asset, long-only teaching backtest."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .exceptions import ConfigurationError, DataValidationError
from .strategy import Signal


@dataclass(frozen=True)
class Trade:
    """One completed long trade."""

    trade_id: int
    entry_timestamp: str
    entry_price: float
    exit_timestamp: str
    exit_price: float
    quantity: float
    entry_fee: float
    exit_fee: float
    gross_pnl: float
    net_pnl: float
    return_pct: float
    bars_held: int
    exit_reason: str


@dataclass(frozen=True)
class BacktestSummary:
    """Stable aggregate metrics for one run."""

    initial_cash: float
    final_equity: float
    total_return_pct: float
    benchmark_return_pct: float
    excess_return_pct: float
    max_drawdown_pct: float
    completed_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float | None
    profit_factor: float | None
    total_fees: float
    exposure_pct: float
    open_position: bool


@dataclass(frozen=True)
class BacktestResult:
    """Aggregate metrics plus row-level outputs."""

    summary: BacktestSummary
    equity_curve: list[dict[str, float | str]]
    trades: list[Trade]


@dataclass(frozen=True)
class _OpenPosition:
    timestamp: str
    price: float
    quantity: float
    fee: float
    index: int


def _validate_parameters(initial_cash: float, fee_rate: float, slippage_rate: float) -> None:
    if not math.isfinite(initial_cash) or initial_cash <= 0:
        raise ConfigurationError("Initial cash must be a finite number greater than 0")
    for name, value in (("fee rate", fee_rate), ("slippage rate", slippage_rate)):
        if not math.isfinite(value) or value < 0 or value >= 1:
            raise ConfigurationError(f"{name.capitalize()} must be at least 0 and below 1")


def _build_trade(
    position: _OpenPosition,
    signal: Signal,
    index: int,
    exit_price: float,
    exit_fee: float,
    exit_reason: str,
    trade_id: int,
) -> Trade:
    gross_pnl = (exit_price - position.price) * position.quantity
    net_pnl = gross_pnl - position.fee - exit_fee
    invested = position.price * position.quantity + position.fee
    return_pct = (net_pnl / invested) * 100
    return Trade(
        trade_id=trade_id,
        entry_timestamp=position.timestamp,
        entry_price=round(position.price, 8),
        exit_timestamp=signal.timestamp,
        exit_price=round(exit_price, 8),
        quantity=round(position.quantity, 10),
        entry_fee=round(position.fee, 8),
        exit_fee=round(exit_fee, 8),
        gross_pnl=round(gross_pnl, 8),
        net_pnl=round(net_pnl, 8),
        return_pct=round(return_pct, 6),
        bars_held=index - position.index,
        exit_reason=exit_reason,
    )


def run_long_only_backtest(
    signals: list[Signal],
    initial_cash: float = 10_000.0,
    fee_rate: float = 0.001,
    slippage_rate: float = 0.0005,
    close_position_at_end: bool = True,
) -> BacktestResult:
    """Run an all-in/all-out long-only backtest using current-close execution."""
    _validate_parameters(initial_cash, fee_rate, slippage_rate)
    if not signals:
        raise DataValidationError("Cannot run a backtest with empty signals")
    for index, signal in enumerate(signals):
        if not math.isfinite(signal.close) or signal.close <= 0:
            raise DataValidationError(
                f"Invalid close price at signal index {index}: {signal.close!r}"
            )

    cash = initial_cash
    quantity = 0.0
    position: _OpenPosition | None = None
    cumulative_fees = 0.0
    peak_equity = initial_cash
    max_drawdown_pct = 0.0
    exposure_bars = 0
    trades: list[Trade] = []
    equity_curve: list[dict[str, float | str]] = []
    first_close = signals[0].close

    for index, signal in enumerate(signals):
        action = "hold"
        price = signal.close

        if signal.action == "buy" and quantity == 0 and cash > 0:
            execution_price = price * (1 + slippage_rate)
            quantity = cash / (execution_price * (1 + fee_rate))
            notional = quantity * execution_price
            entry_fee = notional * fee_rate
            cash -= notional + entry_fee
            if abs(cash) < 1e-9:
                cash = 0.0
            cumulative_fees += entry_fee
            position = _OpenPosition(
                timestamp=signal.timestamp,
                price=execution_price,
                quantity=quantity,
                fee=entry_fee,
                index=index,
            )
            action = "buy"
        elif signal.action == "sell" and quantity > 0 and position is not None:
            execution_price = price * (1 - slippage_rate)
            proceeds = quantity * execution_price
            exit_fee = proceeds * fee_rate
            cash += proceeds - exit_fee
            cumulative_fees += exit_fee
            trades.append(
                _build_trade(
                    position,
                    signal,
                    index,
                    execution_price,
                    exit_fee,
                    "signal",
                    len(trades) + 1,
                )
            )
            quantity = 0.0
            position = None
            action = "sell"

        if quantity > 0:
            exposure_bars += 1
        equity = cash + quantity * price
        peak_equity = max(peak_equity, equity)
        drawdown_pct = ((peak_equity - equity) / peak_equity) * 100
        max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
        equity_curve.append(
            {
                "timestamp": signal.timestamp,
                "close": round(price, 8),
                "short_ma": "" if signal.short_ma is None else round(signal.short_ma, 8),
                "long_ma": "" if signal.long_ma is None else round(signal.long_ma, 8),
                "signal": signal.action,
                "executed_action": action,
                "cash": round(cash, 8),
                "asset_qty": round(quantity, 10),
                "equity": round(equity, 8),
                "benchmark_equity": round(initial_cash * price / first_close, 8),
                "peak_equity": round(peak_equity, 8),
                "drawdown_pct": round(drawdown_pct, 6),
                "cumulative_fees": round(cumulative_fees, 8),
            }
        )

    if close_position_at_end and quantity > 0 and position is not None:
        final_signal = signals[-1]
        execution_price = final_signal.close * (1 - slippage_rate)
        proceeds = quantity * execution_price
        exit_fee = proceeds * fee_rate
        cash += proceeds - exit_fee
        cumulative_fees += exit_fee
        trades.append(
            _build_trade(
                position,
                final_signal,
                len(signals) - 1,
                execution_price,
                exit_fee,
                "end_of_data",
                len(trades) + 1,
            )
        )
        quantity = 0.0
        position = None
        final_equity = cash
        peak_equity = max(peak_equity, final_equity)
        drawdown_pct = ((peak_equity - final_equity) / peak_equity) * 100
        max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)
        row = equity_curve[-1]
        row["executed_action"] = (
            "end_of_data_sell"
            if row["executed_action"] == "hold"
            else f"{row['executed_action']}+end_of_data_sell"
        )
        row["cash"] = round(cash, 8)
        row["asset_qty"] = 0.0
        row["equity"] = round(final_equity, 8)
        row["peak_equity"] = round(peak_equity, 8)
        row["drawdown_pct"] = round(drawdown_pct, 6)
        row["cumulative_fees"] = round(cumulative_fees, 8)

    final_equity = cash + quantity * signals[-1].close
    total_return_pct = ((final_equity - initial_cash) / initial_cash) * 100
    benchmark_return_pct = ((signals[-1].close - first_close) / first_close) * 100
    winning = sum(trade.net_pnl > 0 for trade in trades)
    losing = sum(trade.net_pnl < 0 for trade in trades)
    win_rate = (winning / len(trades) * 100) if trades else None
    gross_profit = sum(max(trade.net_pnl, 0.0) for trade in trades)
    gross_loss = abs(sum(min(trade.net_pnl, 0.0) for trade in trades))
    profit_factor = gross_profit / gross_loss if trades and gross_loss > 0 else None

    return BacktestResult(
        summary=BacktestSummary(
            initial_cash=round(initial_cash, 8),
            final_equity=round(final_equity, 8),
            total_return_pct=round(total_return_pct, 6),
            benchmark_return_pct=round(benchmark_return_pct, 6),
            excess_return_pct=round(total_return_pct - benchmark_return_pct, 6),
            max_drawdown_pct=round(max_drawdown_pct, 6),
            completed_trades=len(trades),
            winning_trades=winning,
            losing_trades=losing,
            win_rate_pct=None if win_rate is None else round(win_rate, 6),
            profit_factor=None if profit_factor is None else round(profit_factor, 6),
            total_fees=round(cumulative_fees, 8),
            exposure_pct=round(exposure_bars / len(signals) * 100, 6),
            open_position=quantity > 0,
        ),
        equity_curve=equity_curve,
        trades=trades,
    )
