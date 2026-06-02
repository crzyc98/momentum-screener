"""Pure, deterministic technical indicators.

Every function takes a price Series (typically adjusted Close, oldest->newest)
and returns plain floats or ``None`` when there isn't enough history. No I/O,
no global state — these are the unit-tested core of the engine.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_MONTH = 21
TRADING_DAYS_PER_YEAR = 252


def sma(close: pd.Series, window: int) -> float | None:
    """Latest simple moving average over ``window`` periods."""
    if len(close) < window:
        return None
    return float(close.iloc[-window:].mean())


def sma_series(close: pd.Series, window: int) -> pd.Series:
    """Full rolling SMA series (used by the backtester / charts)."""
    return close.rolling(window).mean()


def rsi(close: pd.Series, period: int = 14) -> float | None:
    """Wilder's RSI of the latest bar. Returns None if history is too short."""
    if len(close) < period + 1:
        return None
    delta = close.diff().dropna()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)
    # Wilder's smoothing via exponential mean with alpha = 1/period.
    avg_gain = gains.ewm(alpha=1 / period, adjust=False).mean().iloc[-1]
    avg_loss = losses.ewm(alpha=1 / period, adjust=False).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return float(100.0 - (100.0 / (1.0 + rs)))


def pct_from_52w_high(close: pd.Series, window: int = TRADING_DAYS_PER_YEAR) -> float | None:
    """Fractional distance below the trailing high (<= 0). -0.05 means 5% below."""
    if len(close) < 2:
        return None
    window = min(window, len(close))
    high = float(close.iloc[-window:].max())
    if high <= 0:
        return None
    return float(close.iloc[-1] / high - 1.0)


def total_return(close: pd.Series, lookback_days: int, skip_days: int = 0) -> float | None:
    """Total return over ``lookback_days``, ending ``skip_days`` before the last bar.

    Skipping the most recent few days dodges short-term mean-reversion noise.
    """
    end_idx = -1 - skip_days
    start_idx = end_idx - lookback_days
    if len(close) < abs(start_idx):
        return None
    start = float(close.iloc[start_idx])
    end = float(close.iloc[end_idx])
    if start <= 0:
        return None
    return float(end / start - 1.0)


def composite_momentum(
    close: pd.Series,
    lookbacks_months: list[int],
    skip_days: int = 5,
) -> float | None:
    """Mean of total returns over each lookback window (in months).

    Returns None unless *every* requested lookback has enough history, so the
    composite is always an apples-to-apples blend.
    """
    rets: list[float] = []
    for months in lookbacks_months:
        r = total_return(close, months * TRADING_DAYS_PER_MONTH, skip_days)
        if r is None:
            return None
        rets.append(r)
    if not rets:
        return None
    return float(np.mean(rets))


def avg_dollar_volume(close: pd.Series, volume: pd.Series, window: int = 20) -> float | None:
    """Average daily dollar volume over the trailing window."""
    if len(close) < window or len(volume) < window:
        return None
    dollar = (close.iloc[-window:] * volume.iloc[-window:]).mean()
    if pd.isna(dollar):
        return None
    return float(dollar)
