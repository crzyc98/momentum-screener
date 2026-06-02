"""The funnel gates: liquidity/size, fundamental quality, technical/momentum.

Each ``passes_*`` function returns ``(ok, reason)`` where ``reason`` is empty on
pass and a human-readable explanation on fail — that string is what lands in the
audit trail. Cross-sectional cutoffs (P/CF quartile, quality tier) are computed
once over the liquidity-passed universe by :func:`fundamental_thresholds`.

Missing data fails the relevant gate explicitly (never silently passes). If
yfinance's spotty forward-EPS coverage drops too many names, relax the dial in
``config/strategy.yaml`` rather than guessing values here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from momentum.config import FundamentalConfig, TechnicalConfig, UniverseConfig


# --------------------------------------------------------------- liquidity/size
def passes_liquidity(row: pd.Series, cfg: UniverseConfig) -> tuple[bool, str]:
    if pd.isna(row.get("market_cap")):
        return False, "missing market cap"
    if row["market_cap"] < cfg.market_cap_floor:
        return False, f"market cap ${row['market_cap']/1e9:.1f}B < ${cfg.market_cap_floor/1e9:.0f}B floor"
    if pd.isna(row.get("price")) or row["price"] < cfg.min_price:
        return False, f"price ${row.get('price')} < ${cfg.min_price} floor"
    if pd.isna(row.get("adv")) or row["adv"] < cfg.min_avg_dollar_volume:
        return False, f"avg $ volume < ${cfg.min_avg_dollar_volume/1e6:.0f}M floor"
    return True, ""


# ------------------------------------------------------------------ quality proxy
def _zscore(s: pd.Series) -> pd.Series:
    std = s.std(ddof=0)
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=s.index)
    return (s - s.mean()) / std


def quality_score(df: pd.DataFrame) -> pd.Series:
    """Deterministic quality proxy: mean z-score of ROE, operating margin, and
    inverse leverage over the given (liquidity-passed) universe. yfinance has no
    S&P Global quality score, so this stands in for it — documented in README."""
    roe = _zscore(df["roe"].astype(float))
    opm = _zscore(df["op_margin"].astype(float))
    lev = -_zscore(df["dte"].astype(float))  # lower debt/equity is better
    return pd.concat([roe, opm, lev], axis=1).mean(axis=1, skipna=True)


@dataclass(frozen=True)
class FundamentalThresholds:
    pcf_cutoff: float | None        # pass if P/CF <= cutoff (lowest quartile)
    quality_cutoff: float | None    # pass if quality_score >= cutoff


def fundamental_thresholds(df: pd.DataFrame, cfg: FundamentalConfig) -> FundamentalThresholds:
    """Cross-sectional cutoffs computed over the liquidity-passed universe."""
    pcf = df["pcf"].dropna()
    pcf_cutoff = float(pcf.quantile(cfg.pcf_quantile)) if len(pcf) else None
    qs = df["quality_score"].dropna()
    quality_cutoff = float(qs.quantile(1.0 - cfg.quality_quantile)) if len(qs) else None
    return FundamentalThresholds(pcf_cutoff=pcf_cutoff, quality_cutoff=quality_cutoff)


def passes_fundamental(
    row: pd.Series, cfg: FundamentalConfig, thr: FundamentalThresholds
) -> tuple[bool, str]:
    if cfg.require_positive_trailing_eps_growth:
        eg = row.get("earnings_growth")
        if pd.isna(eg):
            return False, "missing trailing earnings growth"
        if eg <= 0:
            return False, f"trailing earnings growth {eg:.1%} <= 0"
    if cfg.require_positive_forward_eps_growth:
        fg = row.get("fwd_eps_growth")
        if pd.isna(fg):
            return False, "missing forward EPS growth"
        if fg <= 0:
            return False, f"forward EPS growth {fg:.1%} <= 0"
    if cfg.pcf_top_quartile:
        pcf = row.get("pcf")
        if pd.isna(pcf):
            return False, "missing / non-positive cash flow (P/CF)"
        if thr.pcf_cutoff is not None and pcf > thr.pcf_cutoff:
            return False, f"P/CF {pcf:.1f} above top-quartile cutoff {thr.pcf_cutoff:.1f}"
    if cfg.quality_top_tier:
        qs = row.get("quality_score")
        if pd.isna(qs):
            return False, "missing quality inputs"
        if thr.quality_cutoff is not None and qs < thr.quality_cutoff:
            return False, "quality proxy below top-tier cutoff"
    return True, ""


# ---------------------------------------------------------------------- technical
def passes_technical(row: pd.Series, cfg: TechnicalConfig) -> tuple[bool, str]:
    price, sma50, sma200 = row.get("price"), row.get("sma50"), row.get("sma200")
    if any(pd.isna(x) for x in (price, sma50, sma200)):
        return False, "insufficient price history for SMAs"
    if cfg.price_above_50sma and not (price > sma50):
        return False, "price below 50-day SMA"
    if cfg.golden_cross_50_over_200 and not (sma50 > sma200):
        return False, "50-SMA below 200-SMA (no golden-cross regime)"
    off_high = row.get("pct_off_high")
    if pd.isna(off_high):
        return False, "missing 52-week high"
    if off_high < -cfg.within_pct_of_52w_high:
        return False, f"{abs(off_high):.1%} below 52-wk high (> {cfg.within_pct_of_52w_high:.0%})"
    return True, ""
