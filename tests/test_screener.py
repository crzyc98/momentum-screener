"""End-to-end funnel on the FakeProvider: determinism, ranking, HALO-non-gating."""

from __future__ import annotations

import copy

from momentum.config import load_config
from momentum.screener import run_screen

TICKERS = [f"T{i:02d}" for i in range(10)]


def _cfg():
    cfg = load_config("config/strategy.yaml")
    # The synthetic universe is only 10 names with identical profitability; keep the
    # whole set (quality top-half cutoff = the common value) so the funnel exercises
    # selection/ranking rather than an arbitrary tie-break.
    cfg.fundamental.quality_quantile = 1.0
    cfg.universe.min_avg_dollar_volume = 1_000_000
    return cfg


def test_screen_selects_and_ranks(fake_provider, as_of):
    cfg = _cfg()
    result = run_screen(fake_provider, TICKERS, as_of, cfg)
    assert len(result.selected) > 0
    # Higher-drift names (higher index) should rank first by composite momentum.
    ranks = result.selected.sort_values("rank")["ticker"].tolist()
    assert ranks[0] == "T09"
    # momentum strictly non-increasing down the ranking
    moms = result.selected.sort_values("rank")["momentum"].tolist()
    assert all(moms[i] >= moms[i + 1] for i in range(len(moms) - 1))


def test_screen_is_deterministic(fake_provider, as_of):
    cfg = _cfg()
    r1 = run_screen(fake_provider, TICKERS, as_of, cfg)
    r2 = run_screen(fake_provider, TICKERS, as_of, cfg)
    assert r1.selected["ticker"].tolist() == r2.selected["ticker"].tolist()
    assert r1.selected["momentum"].tolist() == r2.selected["momentum"].tolist()


def test_halo_is_observational_not_gating(fake_provider, as_of):
    """Flipping the HALO sector set must NOT change which names are selected."""
    cfg_a = _cfg()
    cfg_b = copy.deepcopy(cfg_a)
    cfg_b.halo.heavy_asset_sectors = []          # no HALO names at all
    sel_a = run_screen(fake_provider, TICKERS, as_of, cfg_a).selected["ticker"].tolist()
    sel_b = run_screen(fake_provider, TICKERS, as_of, cfg_b).selected["ticker"].tolist()
    assert sel_a == sel_b                          # selection unchanged
    # But the HALO column itself reflects the config.
    halo_a = run_screen(fake_provider, TICKERS, as_of, cfg_a).selected["halo"].any()
    assert halo_a  # at least one heavy-asset sector present under default config


def test_quality_unverified_flag_propagates(fake_provider, as_of):
    """A name that clears the quality floor only because a field was missing must be
    flagged quality_unverified in the selected book (skip policy provenance)."""
    cfg = _cfg()  # default missing_data_policy = skip
    # Blank out a quality field (FCF) for the top-ranked name T09.
    fake_provider._info["T09"]["freeCashflow"] = None
    result = run_screen(fake_provider, TICKERS, as_of, cfg)
    sel = result.selected.set_index("ticker")
    assert "T09" in sel.index                      # still selected (not penalized)
    assert bool(sel.loc["T09", "quality_unverified"]) is True
    assert "fcf" in sel.loc["T09", "skipped_checks"]
    # A name with full data is not flagged.
    assert bool(sel.loc["T08", "quality_unverified"]) is False


def test_audit_covers_every_input(fake_provider, as_of):
    cfg = _cfg()
    result = run_screen(fake_provider, TICKERS, as_of, cfg)
    assert set(result.audit["ticker"]) == set(TICKERS)
    # Every audit row has a stage and a status.
    assert result.audit["stage"].notna().all()
    assert set(result.audit["status"]).issubset({"SELECT", "DROP"})
