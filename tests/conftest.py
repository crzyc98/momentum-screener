"""Shared test fixtures: a deterministic in-memory provider, no network."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest


def make_prices(as_of: date, days: int, start: float, drift: float,
                seed: int = 0) -> pd.DataFrame:
    """Deterministic synthetic OHLCV ending at ``as_of``.

    ``drift`` is per-day geometric drift; positive => uptrend (passes SMAs / near high).
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(end=pd.Timestamp(as_of), periods=days)
    noise = rng.normal(0, 0.001, size=days)  # tiny, deterministic
    rets = drift + noise
    close = start * np.cumprod(1 + rets)
    return pd.DataFrame(
        {"Close": close, "High": close, "Low": close, "Open": close,
         "Volume": np.full(days, 5_000_000.0)},
        index=idx,
    ).rename_axis("Date")


class FakeProvider:
    """Implements the DataProvider protocol from in-memory dicts."""

    def __init__(self, prices: dict[str, pd.DataFrame], info: dict[str, dict]):
        self._prices = prices
        self._info = info

    def price_history(self, ticker: str, as_of: date) -> pd.DataFrame:
        df = self._prices.get(ticker, pd.DataFrame())
        if df.empty:
            return df
        return df[df.index.date <= as_of]

    def info(self, ticker: str, as_of: date) -> dict:
        return self._info.get(ticker, {})


@pytest.fixture
def as_of() -> date:
    return date(2024, 12, 31)


@pytest.fixture
def fake_provider(as_of):
    """Ten uptrending large caps with healthy fundamentals across sectors."""
    sectors = ["Energy", "Industrials", "Technology", "Consumer Defensive",
               "Utilities", "Financial Services", "Basic Materials",
               "Healthcare", "Real Estate", "Consumer Cyclical"]
    prices, info = {}, {}
    for i in range(10):
        tkr = f"T{i:02d}"
        # Vary drift so momentum ranking is unambiguous and deterministic.
        prices[tkr] = make_prices(as_of, days=420, start=50 + i,
                                   drift=0.0006 + i * 0.0001, seed=i)
        ocf = (50e9 + i * 1e9) / 12.0          # P/CF = 12 (well under any ceiling)
        info[tkr] = {
            "marketCap": 50e9 + i * 1e9,
            "sector": sectors[i],
            "trailingEps": 5.0,
            "forwardEps": 6.0,                  # positive forward growth
            "earningsGrowth": 0.15,             # positive trailing
            "operatingCashflow": ocf,
            "freeCashflow": ocf * 0.8,          # FCF > 0
            "netIncomeToCommon": ocf * 0.7,     # OCF >= NI -> accruals_ok
            "returnOnAssets": 0.12,
            "grossMargins": 0.45,
            "operatingMargins": 0.30,
            "totalRevenue": (50e9 + i * 1e9) * 0.5,
            "debtToEquity": 40.0,
        }
    return FakeProvider(prices, info)
