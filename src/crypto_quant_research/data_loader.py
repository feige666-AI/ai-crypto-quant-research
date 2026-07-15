"""Strict CSV loading and validation for local OHLCV research data."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from .exceptions import DataValidationError

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")
NUMERIC_COLUMNS = ("open", "high", "low", "close", "volume")


@dataclass(frozen=True)
class PriceBar:
    """One validated OHLCV row."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class ValidationSummary:
    """Successful input-validation facts shown by the CLI."""

    input_file: str
    rows: int
    start_timestamp: str
    end_timestamp: str
    has_duplicate_timestamps: bool
    timestamps_ascending: bool
    columns_valid: bool
    numeric_values_valid: bool
    ohlc_relations_valid: bool
    status: str


@dataclass(frozen=True)
class ValidationResult:
    """Validated bars and their summary."""

    bars: list[PriceBar]
    summary: ValidationSummary


def _error(path: Path, line: int | None, field: str, value: object, reason: str) -> None:
    location = str(path)
    if line is not None:
        location += f", line {line}"
    raise DataValidationError(f"{location}, field '{field}', value {value!r}: {reason}")


def validate_ohlcv_csv(path: str | Path) -> ValidationResult:
    """Read and fully validate one local OHLCV CSV file."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise DataValidationError(f"Data file not found: {csv_path}")
    if not csv_path.is_file():
        raise DataValidationError(f"Data path is not a regular file: {csv_path}")
    if csv_path.stat().st_size == 0:
        raise DataValidationError(f"CSV file is empty: {csv_path}")

    try:
        file = csv_path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise DataValidationError(f"Cannot open CSV file {csv_path}: {exc}") from exc

    with file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise DataValidationError(f"CSV file has no header: {csv_path}")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise DataValidationError(f"{csv_path}: missing required columns: {', '.join(missing)}")

        seen_timestamps: set[str] = set()
        previous_timestamp: str | None = None
        bars: list[PriceBar] = []
        for line_number, row in enumerate(reader, start=2):
            timestamp = (row.get("timestamp") or "").strip()
            if not timestamp:
                _error(
                    csv_path, line_number, "timestamp", row.get("timestamp"), "must not be empty"
                )
            if timestamp in seen_timestamps:
                _error(csv_path, line_number, "timestamp", timestamp, "duplicate timestamp")
            if previous_timestamp is not None and timestamp < previous_timestamp:
                _error(
                    csv_path, line_number, "timestamp", timestamp, "timestamps are not ascending"
                )

            values: dict[str, float] = {}
            for field in NUMERIC_COLUMNS:
                raw_value = row.get(field)
                try:
                    value = float(raw_value) if raw_value not in (None, "") else math.nan
                except (TypeError, ValueError):
                    _error(csv_path, line_number, field, raw_value, "must be a number")
                if not math.isfinite(value):
                    _error(csv_path, line_number, field, raw_value, "must be a finite number")
                values[field] = value

            for field in ("open", "high", "low", "close"):
                if values[field] <= 0:
                    _error(
                        csv_path, line_number, field, values[field], "price must be greater than 0"
                    )
            if values["volume"] < 0:
                _error(csv_path, line_number, "volume", values["volume"], "must be at least 0")
            if values["high"] < max(values["open"], values["close"], values["low"]):
                _error(
                    csv_path, line_number, "high", values["high"], "is below open, close, or low"
                )
            if values["low"] > min(values["open"], values["close"], values["high"]):
                _error(csv_path, line_number, "low", values["low"], "is above open, close, or high")

            bars.append(PriceBar(timestamp=timestamp, **values))
            seen_timestamps.add(timestamp)
            previous_timestamp = timestamp

    if not bars:
        raise DataValidationError(f"CSV file contains no price rows: {csv_path}")

    return ValidationResult(
        bars=bars,
        summary=ValidationSummary(
            input_file=str(csv_path),
            rows=len(bars),
            start_timestamp=bars[0].timestamp,
            end_timestamp=bars[-1].timestamp,
            has_duplicate_timestamps=False,
            timestamps_ascending=True,
            columns_valid=True,
            numeric_values_valid=True,
            ohlc_relations_valid=True,
            status="valid",
        ),
    )


def read_ohlcv_csv(path: str | Path) -> list[PriceBar]:
    """Return validated OHLCV bars."""
    return validate_ohlcv_csv(path).bars
