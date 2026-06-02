"""Unit tests for the pure indicator functions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from momentum import indicators as ind


def test_sma_basic():
    s = pd.Series([1, 2, 3, 4, 5], dtype=float)
    assert ind.sma(s, 5) == 3.0
    assert ind.sma(s, 2) == 4.5
    assert ind.sma(s, 6) is None  # not enough data


def test_total_return_and_skip():
    # Geometric series: 100 -> 110 -> 121 ... 10% per step.
    s = pd.Series([100 * 1.1 ** i for i in range(11)], dtype=float)
    # Last bar index -1; lookback of 2 steps, no skip.
    r = ind.total_return(s, lookback_days=2, skip_days=0)
    assert abs(r - (1.1 ** 2 - 1)) < 1e-9
    # Skipping one bar shifts the window back but keeps the same span.
    r_skip = ind.total_return(s, lookback_days=2, skip_days=1)
    assert abs(r_skip - (1.1 ** 2 - 1)) < 1e-9
    assert ind.total_return(s, lookback_days=100) is None


def test_pct_from_52w_high():
    s = pd.Series([10, 20, 15], dtype=float)  # high=20, last=15
    assert abs(ind.pct_from_52w_high(s) - (-0.25)) < 1e-9


def test_rsi_all_gains_is_100():
    s = pd.Series(np.arange(1, 30, dtype=float))  # monotonic up
    assert ind.rsi(s, 14) == 100.0


def test_rsi_midrange_for_choppy():
    rng = np.random.default_rng(0)
    s = pd.Series(100 + np.cumsum(rng.normal(0, 1, 200)))
    val = ind.rsi(s, 14)
    assert val is not None and 0 < val < 100


def test_composite_momentum_requires_all_lookbacks():
    s = pd.Series([100 * 1.001 ** i for i in range(300)], dtype=float)
    val = ind.composite_momentum(s, [3, 6, 9], skip_days=5)
    assert val is not None and val > 0
    # Too short for 9-month lookback -> None.
    short = pd.Series([100 * 1.001 ** i for i in range(50)], dtype=float)
    assert ind.composite_momentum(short, [3, 6, 9], skip_days=5) is None


def test_avg_dollar_volume():
    close = pd.Series([10.0] * 25)
    vol = pd.Series([1_000_000.0] * 25)
    assert ind.avg_dollar_volume(close, vol, 20) == 10_000_000.0
