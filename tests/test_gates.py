"""Gate logic on synthetic rows + cross-sectional thresholds."""

from __future__ import annotations

import pandas as pd

from momentum.config import FundamentalConfig, TechnicalConfig, UniverseConfig
from momentum.gates import (
    FundamentalThresholds,
    passes_fundamental,
    passes_liquidity,
    passes_technical,
)

UCFG = UniverseConfig(market_cap_floor=20e9, min_price=5,
                      min_avg_dollar_volume=25e6, adv_lookback_days=20)
TCFG = TechnicalConfig()
FCFG = FundamentalConfig()


def test_liquidity_pass_and_fail():
    ok, _ = passes_liquidity(
        pd.Series({"market_cap": 50e9, "price": 100, "adv": 100e6}), UCFG)
    assert ok
    bad, why = passes_liquidity(
        pd.Series({"market_cap": 5e9, "price": 100, "adv": 100e6}), UCFG)
    assert not bad and "market cap" in why


def test_liquidity_missing_data_fails():
    bad, why = passes_liquidity(
        pd.Series({"market_cap": None, "price": 100, "adv": 100e6}), UCFG)
    assert not bad and "missing market cap" in why


def test_technical_requires_uptrend_and_near_high():
    good = pd.Series({"price": 110, "sma50": 105, "sma200": 100, "pct_off_high": -0.02})
    ok, _ = passes_technical(good, TCFG)
    assert ok

    below_sma = good.copy(); below_sma["price"] = 104
    bad, why = passes_technical(below_sma, TCFG)
    assert not bad and "50-day SMA" in why

    far_from_high = good.copy(); far_from_high["pct_off_high"] = -0.20
    bad2, why2 = passes_technical(far_from_high, TCFG)
    assert not bad2 and "52-wk high" in why2


def test_fundamental_all_three_required():
    thr = FundamentalThresholds(pcf_cutoff=15.0, quality_cutoff=0.0)
    good = pd.Series({"earnings_growth": 0.1, "fwd_eps_growth": 0.1,
                      "pcf": 12.0, "quality_score": 0.5})
    ok, _ = passes_fundamental(good, FCFG, thr)
    assert ok

    neg_eps = good.copy(); neg_eps["earnings_growth"] = -0.1
    bad, why = passes_fundamental(neg_eps, FCFG, thr)
    assert not bad and "earnings growth" in why

    pricey = good.copy(); pricey["pcf"] = 30.0
    bad2, why2 = passes_fundamental(pricey, FCFG, thr)
    assert not bad2 and "P/CF" in why2

    low_q = good.copy(); low_q["quality_score"] = -1.0
    bad3, why3 = passes_fundamental(low_q, FCFG, thr)
    assert not bad3 and "quality" in why3


def test_fundamental_missing_forward_eps_fails_explicitly():
    thr = FundamentalThresholds(pcf_cutoff=15.0, quality_cutoff=0.0)
    row = pd.Series({"earnings_growth": 0.1, "fwd_eps_growth": None,
                     "pcf": 12.0, "quality_score": 0.5})
    bad, why = passes_fundamental(row, FCFG, thr)
    assert not bad and "forward EPS" in why
