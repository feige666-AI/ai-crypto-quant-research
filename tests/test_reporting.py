from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from crypto_quant_research.backtest import run_long_only_backtest
from crypto_quant_research.exceptions import OutputError
from crypto_quant_research.reporting import (
    build_summary_payload,
    write_equity_curve,
    write_signals,
    write_summary,
    write_trades,
)
from crypto_quant_research.strategy import Signal


@pytest.fixture
def sample_signals() -> list[Signal]:
    return [
        Signal("2025-01-01", 100, None, None, "hold"),
        Signal("2025-01-02", 101, 100.5, 100.5, "buy"),
        Signal("2025-01-03", 105, 103, 102, "sell"),
    ]


def test_write_all_reports(tmp_path: Path, sample_signals: list[Signal]) -> None:
    result = run_long_only_backtest(sample_signals)
    signal_path = tmp_path / "nested" / "signals.csv"
    equity_path = tmp_path / "equity.csv"
    trade_path = tmp_path / "trades.csv"
    write_signals(sample_signals, signal_path)
    write_equity_curve(result, equity_path)
    write_trades(result, trade_path)
    assert signal_path.exists() and equity_path.exists() and trade_path.exists()
    with trade_path.open(encoding="utf-8") as file:
        assert next(csv.DictReader(file))["exit_reason"] == "signal"


def test_empty_trades_still_has_header(tmp_path: Path) -> None:
    result = run_long_only_backtest([Signal("2025-01-01", 100, None, None, "hold")])
    path = tmp_path / "trades.csv"
    write_trades(result, path)
    assert path.read_text(encoding="utf-8").startswith("trade_id,")
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1


def test_summary_schema_and_null_metrics(tmp_path: Path) -> None:
    result = run_long_only_backtest([Signal("2025-01-01", 100, None, None, "hold")])
    payload = build_summary_payload(
        result,
        input_file="data/sample.csv",
        data_rows=1,
        start_timestamp="2025-01-01",
        end_timestamp="2025-01-01",
        short_window=1,
        long_window=2,
        fee_rate=0.001,
        slippage_rate=0.0005,
        close_position_at_end=True,
    )
    path = tmp_path / "summary.json"
    write_summary(payload, path)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["data_type"] == "synthetic"
    assert loaded["profit_factor"] is None
    assert loaded["win_rate_pct"] is None
    assert loaded["generated_at"].endswith("+00:00")
    assert loaded["assumptions"]


def test_output_error_for_directory_path(tmp_path: Path, sample_signals: list[Signal]) -> None:
    with pytest.raises(OutputError):
        write_signals(sample_signals, tmp_path)
