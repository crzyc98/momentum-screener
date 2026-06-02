"""Provider protocol + a normalized Fundamentals view.

The engine only ever talks to this interface, so swapping yfinance for a paid
provider later is a drop-in change.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

import pandas as pd


@runtime_checkable
class DataProvider(Protocol):
    """Point-in-time market & fundamental data.

    Implementations MUST be deterministic given an ``as_of`` date: a re-run for
    the same date returns identical data (achieved here via a snapshot cache).
    """

    def price_history(self, ticker: str, as_of: date) -> pd.DataFrame:
        """Daily OHLCV up to and including ``as_of``. Index = dates, cols include
        ``Close`` and ``Volume``. Returns an empty frame if data is unavailable."""
        ...

    def info(self, ticker: str, as_of: date) -> dict:
        """Snapshot of the fundamental/profile fields for ``ticker`` as of date.
        Returns an empty dict if unavailable."""
        ...


@dataclass(frozen=True)
class Fundamentals:
    """Normalized fundamentals derived from a provider ``info`` dict.

    Any field may be ``None`` when the provider lacks it — gates must treat
    missing data explicitly rather than guessing.
    """

    ticker: str
    market_cap: float | None
    sector: str | None
    trailing_eps: float | None
    forward_eps: float | None
    earnings_growth: float | None          # trailing YoY earnings growth
    operating_cashflow: float | None
    free_cashflow: float | None            # cash generation (FCF > 0 is the signal)
    net_income: float | None               # for the accruals check (OCF >= NI)
    return_on_equity: float | None
    return_on_assets: float | None
    operating_margin: float | None
    gross_margin: float | None
    revenue: float | None
    debt_to_equity: float | None
    business_summary: str | None

    @property
    def price_to_cashflow(self) -> float | None:
        """P/CF = market cap / operating cash flow. v1.1: used ONLY as a far-out
        sanity ceiling (exclude blow-off multiples), NOT as a value gate — P/CF is
        a valuation ratio, anti-correlated with momentum, so a top-quartile cut
        would fight the strategy."""
        if self.market_cap is None or not self.operating_cashflow:
            return None
        if self.operating_cashflow <= 0:
            return None  # negative/zero OCF is disqualifying, not "cheap"
        return self.market_cap / self.operating_cashflow

    @property
    def accruals_ok(self) -> bool | None:
        """OCF >= Net Income — earnings backed by real cash (Sloan accruals).
        The correct operationalization of 'cash flow is harder to manipulate'."""
        if self.operating_cashflow is None or self.net_income is None:
            return None
        return self.operating_cashflow >= self.net_income

    @property
    def fcf_margin(self) -> float | None:
        """Free cash flow / revenue — cash-generation quality, momentum-neutral."""
        if self.free_cashflow is None or not self.revenue:
            return None
        return self.free_cashflow / self.revenue

    @property
    def forward_eps_growth(self) -> float | None:
        """Forward EPS growth proxy = (forwardEps - trailingEps) / |trailingEps|."""
        if self.forward_eps is None or self.trailing_eps is None:
            return None
        if self.trailing_eps == 0:
            return None
        return (self.forward_eps - self.trailing_eps) / abs(self.trailing_eps)


def _num(info: dict, key: str) -> float | None:
    val = info.get(key)
    if val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if f != f:  # NaN
        return None
    return f


def extract_fundamentals(ticker: str, info: dict) -> Fundamentals:
    """Map a raw provider ``info`` dict into the normalized view."""
    return Fundamentals(
        ticker=ticker,
        market_cap=_num(info, "marketCap"),
        sector=info.get("sector"),
        trailing_eps=_num(info, "trailingEps"),
        forward_eps=_num(info, "forwardEps"),
        earnings_growth=_num(info, "earningsGrowth"),
        operating_cashflow=_num(info, "operatingCashflow"),
        free_cashflow=_num(info, "freeCashflow"),
        net_income=_num(info, "netIncomeToCommon"),
        return_on_equity=_num(info, "returnOnEquity"),
        return_on_assets=_num(info, "returnOnAssets"),
        operating_margin=_num(info, "operatingMargins"),
        gross_margin=_num(info, "grossMargins"),
        revenue=_num(info, "totalRevenue"),
        debt_to_equity=_num(info, "debtToEquity"),
        business_summary=info.get("longBusinessSummary"),
    )
