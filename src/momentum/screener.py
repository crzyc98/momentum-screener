"""Funnel orchestration: build metrics, run the gates in order, rank survivors.

Produces a ranked survivor table AND a full audit DataFrame (one row per input
ticker, tagged with the stage it dropped at and why) so every selection decision
is reproducible and explainable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from momentum import indicators as ind
from momentum.config import Config
from momentum.gates import (
    QUALITY_CHECKS,
    fundamental_thresholds,
    passes_fundamental,
    passes_liquidity,
    passes_technical,
    quality_score,
)
from momentum.halo import is_halo
from momentum.providers.base import DataProvider, extract_fundamentals

# Funnel stages, in order. Stored on each audit row as where the name dropped.
STAGE_SELECTED = "selected"
STAGE_RANKED_OUT = "ranked_out"  # qualified but outside top-N
STAGE_TECHNICAL = "technical"
STAGE_FUNDAMENTAL = "fundamental"
STAGE_LIQUIDITY = "liquidity"
STAGE_DATA = "data"


@dataclass
class ScreenResult:
    as_of: date
    audit: pd.DataFrame          # every input ticker + stage/reason + metrics
    survivors: pd.DataFrame      # gate-passers ranked by composite momentum
    selected: pd.DataFrame       # top-N survivors actually picked for the book

    @property
    def n_selected(self) -> int:
        return len(self.selected)


def build_metrics(
    provider: DataProvider, tickers: list[str], as_of: date, cfg: Config
) -> pd.DataFrame:
    """Compute the per-ticker metric row for every candidate (no gating yet)."""
    rows: list[dict] = []
    for t in tickers:
        prices = provider.price_history(t, as_of)
        info = provider.info(t, as_of)
        f = extract_fundamentals(t, info)
        row: dict = {
            "ticker": t,
            "sector": f.sector,
            "halo": is_halo(f.sector, cfg.halo),
            "market_cap": f.market_cap,
            "earnings_growth": f.earnings_growth,
            "fwd_eps_growth": f.forward_eps_growth,
            "fcf": f.free_cashflow,
            "accruals_ok": f.accruals_ok,
            "pcf": f.price_to_cashflow,
            "roa": f.return_on_assets,
            "gross_margin": f.gross_margin,
            "op_margin": f.operating_margin,
            "fcf_margin": f.fcf_margin,
        }
        if prices.empty or "Close" not in prices:
            row.update(
                price=None, adv=None, sma50=None, sma200=None,
                rsi=None, pct_off_high=None, momentum=None, has_prices=False,
            )
        else:
            close = prices["Close"].astype(float)
            volume = prices.get("Volume", pd.Series(dtype=float)).astype(float)
            row.update(
                price=float(close.iloc[-1]),
                adv=ind.avg_dollar_volume(close, volume, cfg.universe.adv_lookback_days),
                sma50=ind.sma(close, 50),
                sma200=ind.sma(close, 200),
                rsi=ind.rsi(close, 14),
                pct_off_high=ind.pct_from_52w_high(close),
                momentum=ind.composite_momentum(
                    close, cfg.momentum.lookbacks_months, cfg.momentum.skip_recent_days
                ),
                has_prices=True,
            )
        rows.append(row)
    df = pd.DataFrame(rows).set_index("ticker", drop=False)
    df.index.name = "symbol"  # avoid index/column name clash with the "ticker" column
    return df


def run_screen(
    provider: DataProvider, tickers: list[str], as_of: date, cfg: Config
) -> ScreenResult:
    """Run the full funnel and return survivors + audit."""
    df = build_metrics(provider, tickers, as_of, cfg)
    df["stage"] = STAGE_SELECTED
    df["status"] = "SELECT"
    df["reason"] = ""
    # Provenance for missing_data_policy="skip": which gate fields were skipped, and
    # whether a QUALITY check was among them (i.e. the name cleared the floor unverified).
    df["skipped_checks"] = ""
    df["quality_unverified"] = False

    # Stage 0: data availability.
    no_data = ~df["has_prices"]
    df.loc[no_data, ["stage", "status", "reason"]] = [STAGE_DATA, "DROP", "no price data"]

    # Stage 1: liquidity / size.
    live = df[df["status"] == "SELECT"]
    for t, row in live.iterrows():
        ok, why = passes_liquidity(row, cfg.universe)
        if not ok:
            df.loc[t, ["stage", "status", "reason"]] = [STAGE_LIQUIDITY, "DROP", why]

    # Cross-sectional quality score + thresholds over the liquidity-passed set.
    liq = df[df["status"] == "SELECT"].copy()
    if not liq.empty:
        df.loc[liq.index, "quality_score"] = quality_score(liq)
    else:
        df["quality_score"] = pd.NA
    thr = fundamental_thresholds(df[df["status"] == "SELECT"], cfg.fundamental)

    # Stage 2: fundamental quality.
    for t, row in df[df["status"] == "SELECT"].iterrows():
        ok, why, skipped = passes_fundamental(row, cfg.fundamental, thr)
        if not ok:
            df.loc[t, ["stage", "status", "reason"]] = [STAGE_FUNDAMENTAL, "DROP", why]
        elif skipped:
            df.loc[t, "skipped_checks"] = ",".join(skipped)
            df.loc[t, "quality_unverified"] = any(s in QUALITY_CHECKS for s in skipped)

    # Stage 3: technical / trend structure.
    for t, row in df[df["status"] == "SELECT"].iterrows():
        ok, why = passes_technical(row, cfg.technical)
        if not ok:
            df.loc[t, ["stage", "status", "reason"]] = [STAGE_TECHNICAL, "DROP", why]

    # Stage 4: rank qualifiers by composite momentum. Missing momentum can't rank.
    qual = df[df["status"] == "SELECT"].copy()
    missing_mom = qual["momentum"].isna()
    for t in qual[missing_mom].index:
        df.loc[t, ["stage", "status", "reason"]] = [
            STAGE_TECHNICAL, "DROP", "insufficient history for composite momentum"
        ]
    qual = df[df["status"] == "SELECT"].copy()

    # Deterministic sort: momentum desc, ticker asc as tie-break (NOT halo in v1).
    qual = qual.sort_values(["momentum", "ticker"], ascending=[False, True])
    qual["rank"] = range(1, len(qual) + 1)
    df.loc[qual.index, "rank"] = qual["rank"].values

    # Top-N cut → the rest are ranked_out (still "qualified", just oversubscribed).
    n_max = cfg.portfolio.n_max
    if len(qual) > n_max:
        overflow = qual.index[n_max:]
        df.loc[overflow, ["stage", "status", "reason"]] = [
            STAGE_RANKED_OUT, "DROP", f"qualified but outside top-{n_max} by momentum"
        ]

    survivors = (
        df[df["rank"].notna()]
        .sort_values("rank")
        .copy()
    )
    selected = df[df["status"] == "SELECT"].sort_values("rank").copy()
    return ScreenResult(as_of=as_of, audit=df, survivors=survivors, selected=selected)
