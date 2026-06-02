"""The funnel gates: liquidity/size, fundamental quality, technical/momentum.

Each ``passes_*`` function returns ``(ok, reason)`` where ``reason`` is empty on
pass and a human-readable explanation on fail — that string is what lands in the
audit trail. The cross-sectional profitability cutoff is computed once over the
liquidity-passed universe by :func:`fundamental_thresholds`.

Fundamental gate is momentum-COMPATIBLE quality (cash generation + accruals +
profitability), not valuation — see the v1.1 note in ``config/strategy.yaml``.
Missing-data handling follows ``missing_data_policy`` (skip vs fail).
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


# ------------------------------------------------------------ profitability quality
def _zscore(s: pd.Series) -> pd.Series:
    std = s.std(ddof=0)
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=s.index)
    return (s - s.mean()) / std


def quality_score(df: pd.DataFrame) -> pd.Series:
    """Momentum-NEUTRAL profitability proxy (Novy-Marx / QMJ style): mean z-score
    of ROA, gross margin, and operating margin over the liquidity-passed universe.

    Profitability isn't anti-correlated with price strength the way cheapness is,
    so it stacks cleanly on momentum. Stands in for the S&P Global quality score
    that yfinance lacks (the Fidelity field map uses S&P Global directly)."""
    roa = _zscore(df["roa"].astype(float))
    gm = _zscore(df["gross_margin"].astype(float))
    opm = _zscore(df["op_margin"].astype(float))
    return pd.concat([roa, gm, opm], axis=1).mean(axis=1, skipna=True)


@dataclass(frozen=True)
class FundamentalThresholds:
    quality_cutoff: float | None    # pass if quality_score >= cutoff (top-half profitability)


def fundamental_thresholds(df: pd.DataFrame, cfg: FundamentalConfig) -> FundamentalThresholds:
    """Cross-sectional quality cutoff over the liquidity-passed universe."""
    qs = df["quality_score"].dropna()
    quality_cutoff = float(qs.quantile(1.0 - cfg.quality_quantile)) if len(qs) else None
    return FundamentalThresholds(quality_cutoff=quality_cutoff)


# Checks whose absence means a name cleared the QUALITY floor on unverified data.
QUALITY_CHECKS = frozenset({"fcf", "accruals", "profitability"})


def passes_fundamental(
    row: pd.Series, cfg: FundamentalConfig, thr: FundamentalThresholds
) -> tuple[bool, str, list[str]]:
    """Momentum-compatible quality gate: earnings strength + cash generation +
    accruals quality + profitability. Cash flow is treated as *quality*, not
    *valuation* (P/CF is only a far-out sanity ceiling).

    Returns ``(ok, reason, skipped)``. Under ``missing_data_policy == "skip"`` a
    missing field is recorded in ``skipped`` (the check is not held against the
    name) rather than failing it — so callers can flag any name that qualified
    only because a gate field was absent (see :data:`QUALITY_CHECKS`)."""
    fail_on_missing = cfg.missing_data_policy == "fail"
    skipped: list[str] = []

    def gap(key: str, label: str) -> tuple[bool, str, list[str]] | None:
        """Handle a missing field: fail (strict) or record-and-continue (skip)."""
        if fail_on_missing:
            return False, f"missing {label}", skipped
        skipped.append(key)
        return None

    if cfg.require_positive_trailing_eps_growth:
        eg = row.get("earnings_growth")
        if pd.isna(eg):
            if (m := gap("trailing_eps", "trailing earnings growth")):
                return m
        elif eg <= 0:
            return False, f"trailing earnings growth {eg:.1%} <= 0", skipped
    if cfg.require_positive_forward_eps_growth:
        fg = row.get("fwd_eps_growth")
        if pd.isna(fg):
            if (m := gap("forward_eps", "forward EPS growth")):
                return m
        elif fg <= 0:
            return False, f"forward EPS growth {fg:.1%} <= 0", skipped
    if cfg.require_positive_fcf:
        fcf = row.get("fcf")
        if pd.isna(fcf):
            if (m := gap("fcf", "free cash flow")):
                return m
        elif fcf <= 0:
            return False, "FCF <= 0 (no cash generation)", skipped
    if cfg.require_ocf_ge_net_income:
        acc = row.get("accruals_ok")
        if pd.isna(acc):
            if (m := gap("accruals", "accruals (OCF vs net income)")):
                return m
        elif not acc:
            return False, "OCF < net income (weak accruals quality)", skipped
    if cfg.quality_top_tier:
        qs = row.get("quality_score")
        if pd.isna(qs):
            if (m := gap("profitability", "profitability inputs")):
                return m
        elif thr.quality_cutoff is not None and qs < thr.quality_cutoff:
            return False, "profitability below top-half cutoff", skipped
    if cfg.pcf_ceiling is not None:
        pcf = row.get("pcf")
        # Ceiling only — a present, absurd multiple is excluded; missing P/CF never fails here.
        if not pd.isna(pcf) and pcf > cfg.pcf_ceiling:
            return False, f"P/CF {pcf:.1f} above sanity ceiling {cfg.pcf_ceiling:.0f}", skipped
    return True, "", skipped


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
