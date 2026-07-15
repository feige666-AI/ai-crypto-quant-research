from __future__ import annotations

import pytest

from crypto_quant_research.backtest import run_long_only_backtest
from crypto_quant_research.exceptions import ConfigurationError, DataValidationError
from crypto_quant_research.strategy import Signal


def signals(actions: list[str], closes: list[float]) -> list[Signal]:
    return [
        Signal(f"2025-01-{index + 1:02d}", close, close, close, action)
        for index, (action, close) in enumerate(zip(actions, closes, strict=True))
    ]


@pytest.mark.parametrize(
    "cash,fee,slippage",
    [(0, 0, 0), (-1, 0, 0), (10_000, -0.1, 0), (10_000, 1, 0), (10_000, 0, -1)],
)
def test_invalid_parameters(cash: float, fee: float, slippage: float) -> None:
    with pytest.raises(ConfigurationError):
        run_long_only_backtest(signals(["hold"], [100]), cash, fee, slippage)


def test_empty_signals() -> None:
    with pytest.raises(DataValidationError, match="empty"):
        run_long_only_backtest([])


@pytest.mark.parametrize("price", [0, -1, float("nan"), float("inf")])
def test_invalid_price(price: float) -> None:
    with pytest.raises(DataValidationError, match="Invalid close"):
        run_long_only_backtest(signals(["hold"], [price]))


def test_no_trade_metrics_are_explicit() -> None:
    result = run_long_only_backtest(signals(["hold", "sell", "hold"], [100, 101, 99]))
    assert result.summary.final_equity == 10_000
    assert result.summary.completed_trades == 0
    assert result.summary.win_rate_pct is None
    assert result.summary.profit_factor is None
    assert result.summary.exposure_pct == 0


def test_profitable_trade_without_costs() -> None:
    result = run_long_only_backtest(
        signals(["buy", "hold", "sell"], [100, 110, 120]),
        fee_rate=0,
        slippage_rate=0,
    )
    assert result.summary.final_equity == pytest.approx(12_000)
    assert result.summary.completed_trades == 1
    assert result.summary.winning_trades == 1
    assert result.summary.win_rate_pct == 100
    assert result.summary.profit_factor is None
    assert result.trades[0].gross_pnl == pytest.approx(2_000)


def test_fees_reduce_result() -> None:
    no_fee = run_long_only_backtest(signals(["buy", "sell"], [100, 110]), fee_rate=0)
    with_fee = run_long_only_backtest(signals(["buy", "sell"], [100, 110]), fee_rate=0.01)
    assert with_fee.summary.final_equity < no_fee.summary.final_equity
    assert with_fee.summary.total_fees > 0


def test_slippage_reduces_result() -> None:
    baseline = run_long_only_backtest(signals(["buy", "sell"], [100, 110]), slippage_rate=0)
    slipped = run_long_only_backtest(signals(["buy", "sell"], [100, 110]), slippage_rate=0.01)
    assert slipped.summary.final_equity < baseline.summary.final_equity


def test_drawdown_and_benchmark() -> None:
    result = run_long_only_backtest(
        signals(["buy", "hold", "sell"], [100, 80, 90]), fee_rate=0, slippage_rate=0
    )
    assert result.summary.max_drawdown_pct == pytest.approx(20)
    assert result.summary.benchmark_return_pct == pytest.approx(-10)
    assert result.summary.excess_return_pct == pytest.approx(0)


def test_profit_factor_with_win_and_loss() -> None:
    result = run_long_only_backtest(
        signals(["buy", "sell", "buy", "sell"], [100, 120, 100, 90]),
        fee_rate=0,
        slippage_rate=0,
    )
    assert result.summary.completed_trades == 2
    assert result.summary.winning_trades == 1
    assert result.summary.losing_trades == 1
    assert result.summary.win_rate_pct == 50
    assert result.summary.profit_factor is not None


def test_open_position_when_not_forced() -> None:
    result = run_long_only_backtest(
        signals(["buy", "hold"], [100, 105]),
        fee_rate=0,
        slippage_rate=0,
        close_position_at_end=False,
    )
    assert result.summary.open_position is True
    assert result.summary.completed_trades == 0
    assert result.summary.final_equity == pytest.approx(10_500)


def test_force_close_at_end() -> None:
    result = run_long_only_backtest(
        signals(["buy", "hold"], [100, 105]),
        fee_rate=0,
        slippage_rate=0,
        close_position_at_end=True,
    )
    assert result.summary.open_position is False
    assert result.summary.completed_trades == 1
    assert result.trades[0].exit_reason == "end_of_data"
    assert result.equity_curve[-1]["executed_action"] == "end_of_data_sell"


def test_duplicate_buy_and_empty_sell_are_ignored() -> None:
    result = run_long_only_backtest(
        signals(["sell", "buy", "buy", "sell"], [100, 100, 110, 120]),
        fee_rate=0,
        slippage_rate=0,
    )
    actions = [row["executed_action"] for row in result.equity_curve]
    assert actions == ["hold", "buy", "hold", "sell"]
    assert result.summary.completed_trades == 1


def test_exposure_percentage() -> None:
    result = run_long_only_backtest(
        signals(["hold", "buy", "hold", "sell"], [100, 100, 100, 100]),
        fee_rate=0,
        slippage_rate=0,
    )
    assert result.summary.exposure_pct == 50
