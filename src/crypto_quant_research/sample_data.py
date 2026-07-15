"""Generate deterministic synthetic OHLCV data for the repository demo."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path


def generate_rows(row_count: int = 300, seed: int = 42) -> list[dict[str, str]]:
    """Return reproducible rows with rising, falling, and sideways phases."""
    if row_count < 1:
        raise ValueError("rows must be at least 1")
    randomizer = random.Random(seed)
    current_close = 100.0
    rows: list[dict[str, str]] = []
    start = date(2025, 1, 1)

    for index in range(row_count):
        phase = index / row_count
        if phase < 0.25:
            drift = 0.35
        elif phase < 0.50:
            drift = -0.45
        elif phase < 0.75:
            drift = 0.02
        else:
            drift = 0.28 if index % 18 < 9 else -0.18

        open_price = max(1.0, current_close + randomizer.gauss(0, 0.16))
        close_price = max(1.0, open_price + drift + randomizer.gauss(0, 0.28))
        high_price = max(open_price, close_price) + abs(randomizer.gauss(0.45, 0.16))
        low_price = max(0.01, min(open_price, close_price) - abs(randomizer.gauss(0.42, 0.15)))
        volume = max(0.0, 120 + abs(drift) * 90 + randomizer.gauss(0, 14))
        rows.append(
            {
                "timestamp": (start + timedelta(days=index)).isoformat(),
                "open": f"{open_price:.4f}",
                "high": f"{high_price:.4f}",
                "low": f"{low_price:.4f}",
                "close": f"{close_price:.4f}",
                "volume": f"{volume:.4f}",
            }
        )
        current_close = close_price
    return rows


def write_sample_data(path: str | Path, row_count: int = 300, seed: int = 42) -> Path:
    """Generate and write synthetic OHLCV data."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"]
        )
        writer.writeheader()
        writer.writerows(generate_rows(row_count=row_count, seed=seed))
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate reproducible synthetic OHLCV data.")
    parser.add_argument("--rows", type=int, default=300, help="Number of rows (default: 300)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--output", type=Path, default=Path("data/sample_data.csv"), help="Output CSV path"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = write_sample_data(args.output, row_count=args.rows, seed=args.seed)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"Generated {args.rows} synthetic rows with seed {args.seed}: {output}")
    return 0
