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


def _good_row():
    # FCF>0, OCF>=NI (accruals ok), profitable, sane P/CF, positive EPS growth.
    return pd.Series({"earnings_growth": 0.1, "fwd_eps_growth": 0.1,
                      "fcf": 1e9, "accruals_ok": True, "quality_score": 0.5,
                      "pcf": 12.0})


def test_fundamental_quality_gate_passes_clean_name():
    thr = FundamentalThresholds(quality_cutoff=0.0)
    ok, _, _ = passes_fundamental(_good_row(), FCFG, thr)
    assert ok


def test_fundamental_negative_fcf_fails():
    thr = FundamentalThresholds(quality_cutoff=0.0)
    row = _good_row(); row["fcf"] = -5e8
    bad, why, _ = passes_fundamental(row, FCFG, thr)
    assert not bad and "FCF" in why


def test_fundamental_weak_accruals_fails():
    thr = FundamentalThresholds(quality_cutoff=0.0)
    row = _good_row(); row["accruals_ok"] = False
    bad, why, _ = passes_fundamental(row, FCFG, thr)
    assert not bad and "accruals" in why


def test_fundamental_low_profitability_fails():
    thr = FundamentalThresholds(quality_cutoff=0.0)
    row = _good_row(); row["quality_score"] = -1.0
    bad, why, _ = passes_fundamental(row, FCFG, thr)
    assert not bad and "profitability" in why


def test_pcf_is_ceiling_not_value_gate():
    """A merely-expensive name passes (no top-quartile gate); only blow-off multiples fail."""
    thr = FundamentalThresholds(quality_cutoff=0.0)
    pricey = _good_row(); pricey["pcf"] = 45.0          # expensive but under ceiling 60
    ok, _, _ = passes_fundamental(pricey, FCFG, thr)
    assert ok
    blowoff = _good_row(); blowoff["pcf"] = 120.0        # above ceiling
    bad, why, _ = passes_fundamental(blowoff, FCFG, thr)
    assert not bad and "ceiling" in why


def test_missing_data_policy_skip_vs_fail():
    from momentum.config import FundamentalConfig
    thr = FundamentalThresholds(quality_cutoff=0.0)
    row = _good_row(); row["fwd_eps_growth"] = None      # a yfinance gap

    skip_cfg = FundamentalConfig(missing_data_policy="skip")
    ok, _, _ = passes_fundamental(row, skip_cfg, thr)
    assert ok                                            # gap not held against the name

    fail_cfg = FundamentalConfig(missing_data_policy="fail")
    bad, why, _ = passes_fundamental(row, fail_cfg, thr)
    assert not bad and "forward EPS" in why


def test_skip_records_provenance():
    """Under skip policy, a missing QUALITY field is recorded so it can be flagged."""
    from momentum.config import FundamentalConfig
    from momentum.gates import QUALITY_CHECKS
    thr = FundamentalThresholds(quality_cutoff=0.0)
    row = _good_row(); row["fcf"] = None                 # missing a quality field
    ok, _, skipped = passes_fundamental(row, FundamentalConfig(missing_data_policy="skip"), thr)
    assert ok
    assert "fcf" in skipped
    assert any(s in QUALITY_CHECKS for s in skipped)     # -> would set quality_unverified

    # A clean name skips nothing.
    ok2, _, skipped2 = passes_fundamental(_good_row(), FundamentalConfig(), thr)
    assert ok2 and skipped2 == []
