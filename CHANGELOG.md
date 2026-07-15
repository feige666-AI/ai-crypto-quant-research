# Changelog

## 0.2.0 - 2026-07-16

### Added

- Standard Python package metadata and module entry point.
- `validate`, `signals`, `backtest`, and `demo` CLI commands.
- Strict OHLCV validation and project-specific exceptions.
- Slippage, completed trades, benchmark, exposure, win rate, Profit Factor, and end-of-data handling.
- Reproducible synthetic sample generator, stable CSV/JSON outputs, and three matplotlib charts.
- 77 pytest tests, coverage configuration, Ruff, and multi-version GitHub Actions.
- Baseline audit, backtest assumptions, portfolio walkthrough, interview notes, and verified resume copy.

### Changed

- Rewrote README around the actual local learning workflow and verified commands.
- Expanded project state and technical decisions with explicit safety boundaries.

### Security

- Removed personal absolute paths and the incorrect legacy repository link from current documentation.
- Kept the project offline with no API keys, exchange access, real accounts, or real trades.
