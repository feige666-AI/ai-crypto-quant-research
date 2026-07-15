from __future__ import annotations

import pytest
from conftest import make_bars

from crypto_quant_research.exceptions import ConfigurationError, DataValidationError
from crypto_quant_research.strategy import generate_ma_signals, moving_average


def test_moving_average() -> None:
    assert moving_average([1, 2, 3, 4], 2) == [None, 1.5, 2.5, 3.5]


def test_moving_average_empty() -> None:
    assert moving_average([], 2) == []


def test_invalid_moving_average_window() -> None:
    with pytest.raises(ConfigurationError):
        moving_average([1], 0)


@pytest.mark.parametrize("short,long", [(0, 3), (3, 3), (4, 3)])
def test_invalid_signal_windows(short: int, long: int) -> None:
    with pytest.raises(ConfigurationError):
        generate_ma_signals(make_bars([1, 2, 3, 4, 5]), short, long)


def test_empty_input() -> None:
    with pytest.raises(DataValidationError, match="empty"):
        generate_ma_signals([], 2, 3)


def test_insufficient_input() -> None:
    with pytest.raises(DataValidationError, match="requires at least"):
        generate_ma_signals(make_bars([1, 2]), 2, 3)


def test_first_bullish_relation_is_buy() -> None:
    actions = [signal.action for signal in generate_ma_signals(make_bars([1, 2, 3, 4]), 2, 3)]
    assert actions == ["hold", "hold", "buy", "hold"]


def test_downward_cross_is_sell() -> None:
    actions = [signal.action for signal in generate_ma_signals(make_bars([1, 2, 4, 5, 3, 1]), 2, 3)]
    assert "buy" in actions
    assert "sell" in actions


def test_equal_averages_hold() -> None:
    signals = generate_ma_signals(make_bars([5, 5, 5, 5, 5]), 2, 3)
    assert {signal.action for signal in signals} == {"hold"}


def test_full_uptrend_has_one_entry() -> None:
    actions = [signal.action for signal in generate_ma_signals(make_bars(list(range(1, 11))), 3, 5)]
    assert actions.count("buy") == 1
    assert actions.count("sell") == 0


def test_full_downtrend_has_no_trade_signal() -> None:
    actions = [
        signal.action for signal in generate_ma_signals(make_bars(list(range(10, 0, -1))), 3, 5)
    ]
    assert set(actions) == {"hold"}
