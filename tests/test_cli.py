from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from crypto_quant_research.cli import build_parser, main
from crypto_quant_research.sample_data import write_sample_data


def test_main_help_lists_commands() -> None:
    help_text = build_parser().format_help()
    for command in ("validate", "signals", "backtest", "demo"):
        assert command in help_text


@pytest.mark.parametrize("command", ["validate", "signals", "backtest", "demo"])
def test_subcommand_help(command: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "crypto_quant_research", command, "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "usage:" in completed.stdout.lower()


def test_validate_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data = write_sample_data(tmp_path / "sample.csv", 30, 42)
    assert main(["validate", "--input", str(data)]) == 0
    output = capsys.readouterr().out
    assert "Validation status: valid" in output
    assert "Rows: 30" in output


def test_validate_failure_has_no_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["validate", "--input", str(tmp_path / "missing.csv")]) == 2
    captured = capsys.readouterr()
    assert "error:" in captured.err
    assert "Traceback" not in captured.err


def test_signals_creates_nested_output(tmp_path: Path) -> None:
    data = write_sample_data(tmp_path / "sample.csv", 60, 42)
    output = tmp_path / "nested" / "signals.csv"
    assert (
        main(
            [
                "signals",
                "--input",
                str(data),
                "--short-window",
                "5",
                "--long-window",
                "20",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith("timestamp,close,short_ma,long_ma,signal")


def test_backtest_creates_outputs(tmp_path: Path) -> None:
    data = write_sample_data(tmp_path / "sample.csv", 80, 42)
    equity = tmp_path / "out" / "equity.csv"
    trades = tmp_path / "out" / "trades.csv"
    summary = tmp_path / "out" / "summary.json"
    argv = [
        "backtest",
        "--input",
        str(data),
        "--short-window",
        "5",
        "--long-window",
        "20",
        "--initial-cash",
        "10000",
        "--fee-rate",
        "0.001",
        "--slippage-rate",
        "0.0005",
        "--equity-output",
        str(equity),
        "--trades-output",
        str(trades),
        "--summary-output",
        str(summary),
    ]
    assert main(argv) == 0
    assert equity.exists() and trades.exists() and summary.exists()
    assert json.loads(summary.read_text(encoding="utf-8"))["data_rows"] == 80


def test_demo_creates_repository_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_sample_data(Path("data/sample_data.csv"), 80, 42)
    assert main(["demo"]) == 0
    expected = [
        Path("results/signals_sample.csv"),
        Path("results/equity_curve_sample.csv"),
        Path("results/trades_sample.csv"),
        Path("results/backtest_summary_sample.json"),
        Path("docs/assets/price_and_signals.png"),
        Path("docs/assets/equity_curve.png"),
        Path("docs/assets/drawdown_curve.png"),
    ]
    assert all(path.exists() for path in expected)


def test_invalid_cli_argument_has_nonzero_exit() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "crypto_quant_research", "backtest", "--unknown"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
