"""CSV data loading utilities for local OHLCV research data."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class PriceBar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


def read_ohlcv_csv(path: str | Path) -> list[PriceBar]:
    """Read a small local OHLCV CSV file and validate the expected columns."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        bars: list[PriceBar] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                bars.append(
                    PriceBar(
                        timestamp=str(row["timestamp"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]),
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value at line {line_number}") from exc

    if not bars:
        raise ValueError("CSV file contains no price rows")
    return bars
