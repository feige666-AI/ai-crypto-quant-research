from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_csv

from crypto_quant_research.data_loader import read_ohlcv_csv, validate_ohlcv_csv
from crypto_quant_research.exceptions import DataValidationError


def test_valid_csv_summary(valid_csv: Path) -> None:
    result = validate_ohlcv_csv(valid_csv)
    assert result.summary.rows == 6
    assert result.summary.status == "valid"
    assert result.summary.timestamps_ascending is True
    assert result.bars[0].close == 101


def test_read_returns_bars(valid_csv: Path) -> None:
    assert len(read_ohlcv_csv(valid_csv)) == 6


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(DataValidationError, match="not found"):
        validate_ohlcv_csv(tmp_path / "missing.csv")


def test_directory_is_not_file(tmp_path: Path) -> None:
    with pytest.raises(DataValidationError, match="regular file"):
        validate_ohlcv_csv(tmp_path)


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.touch()
    with pytest.raises(DataValidationError, match="empty"):
        validate_ohlcv_csv(path)


def test_missing_columns(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "missing.csv", [{"timestamp": "2025-01-01"}], ["timestamp"])
    with pytest.raises(DataValidationError, match="missing required columns"):
        validate_ohlcv_csv(path)


def test_header_only_has_no_rows(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "header.csv", [])
    with pytest.raises(DataValidationError, match="no price rows"):
        validate_ohlcv_csv(path)


@pytest.mark.parametrize("bad_value", ["abc", "NaN", "Infinity", "-Infinity", ""])
def test_invalid_numeric_values(
    tmp_path: Path, valid_rows: list[dict[str, object]], bad_value: str
) -> None:
    valid_rows[0]["close"] = bad_value
    path = write_csv(tmp_path / "bad.csv", valid_rows)
    with pytest.raises(DataValidationError, match="field 'close'"):
        validate_ohlcv_csv(path)


@pytest.mark.parametrize("field", ["open", "high", "low", "close"])
def test_non_positive_prices(
    tmp_path: Path, valid_rows: list[dict[str, object]], field: str
) -> None:
    valid_rows[0][field] = -1
    path = write_csv(tmp_path / "bad.csv", valid_rows)
    with pytest.raises(DataValidationError, match="greater than 0"):
        validate_ohlcv_csv(path)


def test_negative_volume(tmp_path: Path, valid_rows: list[dict[str, object]]) -> None:
    valid_rows[0]["volume"] = -1
    with pytest.raises(DataValidationError, match="at least 0"):
        validate_ohlcv_csv(write_csv(tmp_path / "bad.csv", valid_rows))


def test_high_relation(tmp_path: Path, valid_rows: list[dict[str, object]]) -> None:
    valid_rows[0]["high"] = 100
    with pytest.raises(DataValidationError, match="field 'high'"):
        validate_ohlcv_csv(write_csv(tmp_path / "bad.csv", valid_rows))


def test_low_relation(tmp_path: Path, valid_rows: list[dict[str, object]]) -> None:
    valid_rows[0]["low"] = 102
    with pytest.raises(DataValidationError, match="field 'low'"):
        validate_ohlcv_csv(write_csv(tmp_path / "bad.csv", valid_rows))


def test_duplicate_timestamp(tmp_path: Path, valid_rows: list[dict[str, object]]) -> None:
    valid_rows[1]["timestamp"] = valid_rows[0]["timestamp"]
    with pytest.raises(DataValidationError, match="duplicate"):
        validate_ohlcv_csv(write_csv(tmp_path / "bad.csv", valid_rows))


def test_unsorted_timestamp(tmp_path: Path, valid_rows: list[dict[str, object]]) -> None:
    valid_rows[1]["timestamp"] = "2024-12-31"
    with pytest.raises(DataValidationError, match="not ascending"):
        validate_ohlcv_csv(write_csv(tmp_path / "bad.csv", valid_rows))


def test_blank_timestamp(tmp_path: Path, valid_rows: list[dict[str, object]]) -> None:
    valid_rows[0]["timestamp"] = ""
    with pytest.raises(DataValidationError, match="must not be empty"):
        validate_ohlcv_csv(write_csv(tmp_path / "bad.csv", valid_rows))
