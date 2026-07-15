from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from crypto_quant_research.data_loader import validate_ohlcv_csv
from crypto_quant_research.sample_data import generate_rows, main, write_sample_data


def test_generation_is_reproducible() -> None:
    assert generate_rows(20, 42) == generate_rows(20, 42)
    assert generate_rows(20, 42) != generate_rows(20, 43)


def test_generated_ohlc_relationships() -> None:
    for row in generate_rows(30, 7):
        open_price = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        assert high >= max(open_price, close, low)
        assert low <= min(open_price, close, high)
        assert float(row["volume"]) >= 0


def test_invalid_row_count() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        generate_rows(0)


def test_write_and_validate_sample(tmp_path: Path) -> None:
    output = write_sample_data(tmp_path / "data" / "sample.csv", 40, 9)
    result = validate_ohlcv_csv(output)
    assert result.summary.rows == 40
    with output.open(encoding="utf-8") as file:
        assert len(list(csv.DictReader(file))) == 40


def test_generator_cli(tmp_path: Path) -> None:
    output = tmp_path / "sample.csv"
    script = Path(__file__).parents[1] / "scripts" / "generate_sample_data.py"
    completed = subprocess.run(
        [sys.executable, str(script), "--rows", "25", "--seed", "3", "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert output.exists()
    assert "Generated 25 synthetic rows" in completed.stdout


def test_generator_cli_invalid_rows(tmp_path: Path) -> None:
    assert main(["--rows", "0", "--output", str(tmp_path / "sample.csv")]) == 2
