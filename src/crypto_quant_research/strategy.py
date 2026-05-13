"""Simple moving-average signal generation for learning-oriented backtests."""

from __future__ import annotations

from dataclasses import dataclass

from .data_loader import PriceBar


@dataclass(frozen=True)
class Signal:
    timestamp: str
    close: float
    short_ma: float | None
    long_ma: float | None
    action: str


def moving_average(values: list[float], window: int) -> list[float | None]:
    """Calculate a rolling average and return None before the window is ready."""
    if window < 1:
        raise ValueError("Window must be at least 1")

    averages: list[float | None] = []
    rolling_sum = 0.0
    for index, value in enumerate(values):
        rolling_sum += value
        if index >= window:
            rolling_sum -= values[index - window]
        if index + 1 < window:
            averages.append(None)
        else:
            averages.append(rolling_sum / window)
    return averages


def generate_ma_signals(bars: list[PriceBar], short_window: int = 3, long_window: int = 5) -> list[Signal]:
    """Generate buy/sell/hold signals from a basic moving-average crossover."""
    if short_window >= long_window:
        raise ValueError("Short window must be smaller than long window")

    closes = [bar.close for bar in bars]
    short_mas = moving_average(closes, short_window)
    long_mas = moving_average(closes, long_window)
    signals: list[Signal] = []
    previous_relation: int | None = None

    for bar, short_ma, long_ma in zip(bars, short_mas, long_mas):
        action = "hold"
        relation: int | None = None
        if short_ma is not None and long_ma is not None:
            relation = 1 if short_ma > long_ma else -1 if short_ma < long_ma else 0
            if relation > 0 and (previous_relation is None or previous_relation <= 0):
                action = "buy"
            elif relation < 0 and previous_relation is not None and previous_relation >= 0:
                action = "sell"
            previous_relation = relation

        signals.append(
            Signal(
                timestamp=bar.timestamp,
                close=bar.close,
                short_ma=short_ma,
                long_ma=long_ma,
                action=action,
            )
        )
    return signals
