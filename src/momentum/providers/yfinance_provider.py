"""yfinance-backed provider with a dated snapshot cache.

Reproducibility backbone: the first fetch for a given ``as_of`` date writes raw
data to ``<cache_dir>/<as_of>/``; every subsequent run for that date reads the
snapshot instead of hitting the network, so the engine is deterministic and
auditable. Delete a date's cache folder to force a refresh.
"""

from __future__ import annotations

import json
import warnings
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# yfinance is chatty and sometimes warns on delisted/odd tickers; keep runs clean.
warnings.filterwarnings("ignore", category=FutureWarning)

# Subset of yf .info we snapshot — keeps cache small and intent explicit.
_INFO_FIELDS = (
    "marketCap",
    "sector",
    "industry",
    "trailingEps",
    "forwardEps",
    "earningsGrowth",
    "operatingCashflow",
    "freeCashflow",
    "returnOnEquity",
    "operatingMargins",
    "debtToEquity",
    "longBusinessSummary",
)


class YFinanceProvider:
    """Implements the :class:`DataProvider` protocol."""

    def __init__(self, cache_dir: str | Path = "data/cache", history_years: int = 3):
        self.cache_dir = Path(cache_dir)
        self.history_years = history_years

    # ------------------------------------------------------------------ paths
    def _date_dir(self, as_of: date) -> Path:
        d = self.cache_dir / as_of.isoformat()
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _price_path(self, ticker: str, as_of: date) -> Path:
        return self._date_dir(as_of) / f"{ticker.upper()}.prices.csv"

    def _info_path(self, ticker: str, as_of: date) -> Path:
        return self._date_dir(as_of) / f"{ticker.upper()}.info.json"

    # ------------------------------------------------------------- price data
    def price_history(self, ticker: str, as_of: date) -> pd.DataFrame:
        path = self._price_path(ticker, as_of)
        if path.exists():
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            return df
        df = self._fetch_prices(ticker, as_of)
        # Persist even an empty frame so we don't re-hit the network for known gaps.
        df.to_csv(path)
        return df

    def _fetch_prices(self, ticker: str, as_of: date) -> pd.DataFrame:
        import yfinance as yf

        start = (as_of - timedelta(days=int(self.history_years * 365.25) + 5)).isoformat()
        end = (as_of + timedelta(days=1)).isoformat()  # yf end is exclusive
        try:
            raw = yf.download(
                ticker,
                start=start,
                end=end,
                auto_adjust=True,
                progress=False,
                threads=False,
            )
        except Exception:
            return pd.DataFrame()
        if raw is None or raw.empty:
            return pd.DataFrame()
        # yfinance may return a MultiIndex (field, ticker) for single symbols.
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        raw = raw[~raw.index.duplicated(keep="last")].sort_index()
        # Hard guarantee: never leak data after as_of.
        raw = raw[raw.index.date <= as_of]
        raw.index.name = "Date"
        return raw

    # -------------------------------------------------------------- info data
    def info(self, ticker: str, as_of: date) -> dict:
        path = self._info_path(ticker, as_of)
        if path.exists():
            return json.loads(path.read_text())
        info = self._fetch_info(ticker)
        path.write_text(json.dumps(info, indent=2, sort_keys=True, default=str))
        return info

    def _fetch_info(self, ticker: str) -> dict:
        import yfinance as yf

        try:
            raw = yf.Ticker(ticker).info or {}
        except Exception:
            return {}
        return {k: raw.get(k) for k in _INFO_FIELDS if raw.get(k) is not None}
