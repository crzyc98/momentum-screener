"""Smart-Buy allocator: route a contribution to underweights only, no sells."""

from __future__ import annotations

import pandas as pd

from momentum.config import PortfolioConfig
from momentum.portfolio import build_target_book
from momentum.reconstitution import smart_buy_allocation

PCFG = PortfolioConfig(n_max=40, weight_per_name=0.025, min_names_floor=25,
                       cash_ticker="BIL")


def test_smart_buy_rations_proportionally_to_gaps():
    book = build_target_book(["A", "B"], PCFG)  # A,B at 2.5%, BIL 95%
    holdings = pd.DataFrame({
        "ticker": ["A", "B", "BIL"],
        "weight": [0.025, 0.025, 0.95],
        "value": [2500.0, 2500.0, 95000.0],
    })
    alloc = smart_buy_allocation(book, holdings, contribution=10_000)
    # Total allocated equals the contribution (within rounding).
    assert abs(sum(alloc.values()) - 10_000) < 1.0
    # No negative buys (never forces a sell).
    assert all(v >= 0 for v in alloc.values())


def test_smart_buy_skips_without_values():
    book = build_target_book(["A", "B"], PCFG)
    holdings = pd.DataFrame({"ticker": ["A", "B"], "weight": [0.5, 0.5],
                             "value": [pd.NA, pd.NA]})
    assert smart_buy_allocation(book, holdings, contribution=10_000) == {}


def test_smart_buy_skips_without_contribution():
    book = build_target_book(["A"], PCFG)
    holdings = pd.DataFrame({"ticker": ["A"], "weight": [1.0], "value": [1000.0]})
    assert smart_buy_allocation(book, holdings, contribution=0.0) == {}


def test_smart_buy_fills_gaps_then_parks_leftover_in_cash():
    # Tiny gaps, large contribution -> leftover should land in the cash sleeve.
    book = build_target_book(["A"], PCFG)   # A 2.5%, BIL 97.5%
    holdings = pd.DataFrame({
        "ticker": ["A", "BIL"], "weight": [0.025, 0.975],
        "value": [250.0, 9750.0],
    })
    alloc = smart_buy_allocation(book, holdings, contribution=100_000)
    assert "BIL" in alloc and alloc["BIL"] > 0
