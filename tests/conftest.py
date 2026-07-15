from __future__ import annotations

import csv
from pathlib import Path

import pytest

from crypto_quant_research.data_loader import PriceBar


def make_bars(closes: list[float]) -> list[PriceBar]:
    return [
        PriceBar(
            timestamp=f"2025-01-{index + 1:02d}",
            open=close,
            high=close + 1,
            low=close - 1,
            close=close,
            volume=100,
        )
        for index, close in enumerate(closes)
    ]


def write_csv(
    path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None
) -> Path:
    fields = fieldnames or ["timestamp", "open", "high", "low", "close", "volume"]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.fixture
def valid_rows() -> list[dict[str, object]]:
    return [
        {
            "timestamp": f"2025-01-{index + 1:02d}",
            "open": 100 + index,
            "high": 102 + index,
            "low": 99 + index,
            "close": 101 + index,
            "volume": 1000 + index,
        }
        for index in range(6)
    ]


@pytest.fixture
def valid_csv(tmp_path: Path, valid_rows: list[dict[str, object]]) -> Path:
    return write_csv(tmp_path / "valid.csv", valid_rows)
