"""Matplotlib charts for repository documentation."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .backtest import BacktestResult
from .exceptions import OutputError
from .strategy import Signal


def generate_charts(
    signals: list[Signal], result: BacktestResult, output_dir: str | Path
) -> list[Path]:
    """Generate price/signals, equity, and drawdown PNG charts."""
    try:
        os.environ.setdefault(
            "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ai_crypto_quant_matplotlib")
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise OutputError(
            "Chart generation requires matplotlib. Install the project with: pip install -e ."
        ) from exc

    destination = Path(output_dir)
    try:
        destination.mkdir(parents=True, exist_ok=True)
        x_values = list(range(len(signals)))
        closes = [signal.close for signal in signals]
        short_values = [signal.short_ma for signal in signals]
        long_values = [signal.long_ma for signal in signals]

        fig, axis = plt.subplots(figsize=(10, 5))
        axis.plot(x_values, closes, label="Close", linewidth=1.3)
        axis.plot(x_values, short_values, label="Short MA", linewidth=1.0)
        axis.plot(x_values, long_values, label="Long MA", linewidth=1.0)
        for action, marker, color in (("buy", "^", "#15803d"), ("sell", "v", "#b91c1c")):
            points = [
                (index, signal.close)
                for index, signal in enumerate(signals)
                if signal.action == action
            ]
            if points:
                axis.scatter(
                    [point[0] for point in points],
                    [point[1] for point in points],
                    marker=marker,
                    color=color,
                    label=action.title(),
                    zorder=3,
                )
        axis.set_title("Synthetic OHLCV: price and moving-average signals")
        axis.set_xlabel("Synthetic bar index")
        axis.set_ylabel("Price")
        axis.grid(alpha=0.25)
        axis.legend()
        price_path = destination / "price_and_signals.png"
        fig.tight_layout()
        fig.savefig(price_path, dpi=160)
        plt.close(fig)

        fig, axis = plt.subplots(figsize=(10, 5))
        axis.plot(
            [row["equity"] for row in result.equity_curve], label="Strategy equity", linewidth=1.5
        )
        axis.plot(
            [row["benchmark_equity"] for row in result.equity_curve],
            label="Buy-and-hold benchmark",
            linewidth=1.2,
        )
        axis.set_title("Synthetic data: strategy and benchmark equity")
        axis.set_xlabel("Synthetic bar index")
        axis.set_ylabel("Equity")
        axis.grid(alpha=0.25)
        axis.legend()
        equity_path = destination / "equity_curve.png"
        fig.tight_layout()
        fig.savefig(equity_path, dpi=160)
        plt.close(fig)

        fig, axis = plt.subplots(figsize=(10, 4))
        drawdowns = [-float(row["drawdown_pct"]) for row in result.equity_curve]
        axis.fill_between(x_values, drawdowns, 0, color="#dc2626", alpha=0.35)
        axis.plot(x_values, drawdowns, color="#b91c1c", linewidth=1.0)
        axis.set_title("Synthetic data: strategy drawdown")
        axis.set_xlabel("Synthetic bar index")
        axis.set_ylabel("Drawdown (%)")
        axis.grid(alpha=0.25)
        drawdown_path = destination / "drawdown_curve.png"
        fig.tight_layout()
        fig.savefig(drawdown_path, dpi=160)
        plt.close(fig)
    except OSError as exc:
        raise OutputError(f"Cannot write charts to {destination}: {exc}") from exc

    return [price_path, equity_path, drawdown_path]
