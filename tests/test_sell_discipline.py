"""Sell discipline reconciled with the book: a re-selected leader is never sold on
a soft RS wobble (the 'sell the flower' trap); a name out of the book is sold."""

from __future__ import annotations

from datetime import date

import pandas as pd

from momentum.config import load_config
from momentum.screener import ScreenResult
from momentum.sell_discipline import evaluate_holdings
from tests.conftest import FakeProvider, make_prices


def _provider(as_of):
    # SPY rips; AAA (in book) lags it badly over 63d; BBB is just present for prices.
    prices = {
        "SPY": make_prices(as_of, 420, 100, drift=0.0020, seed=1),
        "AAA": make_prices(as_of, 420, 50, drift=0.0004, seed=2),   # underperforms SPY
        "BBB": make_prices(as_of, 420, 50, drift=0.0015, seed=3),
    }
    return FakeProvider(prices, {})


def _result(as_of, selected_tickers, qualified_tickers):
    sel = pd.DataFrame({"ticker": selected_tickers})
    sur = pd.DataFrame({"ticker": qualified_tickers})
    return ScreenResult(as_of=as_of, audit=pd.DataFrame(), survivors=sur, selected=sel)


def test_reselected_leader_with_rs_wobble_is_held_with_warning():
    as_of = date(2024, 12, 31)
    cfg = load_config("config/strategy.yaml")
    provider = _provider(as_of)
    # AAA is in the new top-N book; BBB is not qualified (off-screener).
    result = _result(as_of, selected_tickers=["AAA"], qualified_tickers=["AAA"])
    holdings = pd.DataFrame({"ticker": ["AAA", "BBB"], "weight": [0.5, 0.5],
                             "value": [5000.0, 5000.0]})

    ev = evaluate_holdings(provider, holdings, result, cfg, as_of).set_index("ticker")

    # Re-selected leader: HELD despite tripping RS breakdown -> it's a warning, not a sell.
    assert ev.loc["AAA", "action"] == "HOLD"
    assert "RS breakdown" in ev.loc["AAA", "warnings"]
    assert ev.loc["AAA", "reasons"] == ""

    # Out-of-book name: SOLD, with the membership reason.
    assert ev.loc["BBB", "action"] == "SELL"
    assert "off screener" in ev.loc["BBB", "reasons"]


def test_out_of_book_name_sold_for_rank_drop():
    as_of = date(2024, 12, 31)
    cfg = load_config("config/strategy.yaml")
    provider = _provider(as_of)
    # AAA qualified but NOT in the top-N book -> fell out of rank -> SELL.
    result = _result(as_of, selected_tickers=["BBB"], qualified_tickers=["AAA", "BBB"])
    holdings = pd.DataFrame({"ticker": ["AAA"], "weight": [1.0], "value": [1000.0]})

    ev = evaluate_holdings(provider, holdings, result, cfg, as_of).set_index("ticker")
    assert ev.loc["AAA", "action"] == "SELL"
    assert "top-N momentum rank" in ev.loc["AAA", "reasons"]
