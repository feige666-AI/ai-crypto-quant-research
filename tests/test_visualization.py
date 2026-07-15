from __future__ import annotations

from pathlib import Path

from crypto_quant_research.backtest import run_long_only_backtest
from crypto_quant_research.strategy import Signal
from crypto_quant_research.visualization import generate_charts


def test_generate_three_nonempty_charts(tmp_path: Path) -> None:
    signals = [
        Signal("2025-01-01", 100, None, None, "hold"),
        Signal("2025-01-02", 101, 100.5, None, "hold"),
        Signal("2025-01-03", 103, 102, 101, "buy"),
        Signal("2025-01-04", 99, 101, 101, "sell"),
    ]
    result = run_long_only_backtest(signals)
    paths = generate_charts(signals, result, tmp_path / "assets")
    assert {path.name for path in paths} == {
        "price_and_signals.png",
        "equity_curve.png",
        "drawdown_curve.png",
    }
    assert all(path.stat().st_size > 1_000 for path in paths)
