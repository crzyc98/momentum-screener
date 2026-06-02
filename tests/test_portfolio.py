"""Cash-accordion math: fewer qualifiers => more T-bills, automatically."""

from __future__ import annotations

import pytest

from momentum.config import PortfolioConfig


@pytest.fixture
def pcfg():
    return PortfolioConfig(n_max=40, weight_per_name=0.025, min_names_floor=25,
                           cash_ticker="BIL")


def _tickers(n):
    return [f"T{i:02d}" for i in range(n)]


def test_full_book_no_cash(pcfg):
    from momentum.portfolio import build_target_book
    book = build_target_book(_tickers(40), pcfg)
    assert book.n_equity == 40
    assert book.equity_weight == 1.0
    assert book.cash_weight == 0.0
    assert "BIL" not in book.weights           # no cash sleeve when fully invested
    assert abs(sum(book.weights.values()) - 1.0) < 1e-9
    assert not book.below_floor


def test_partial_book_accordion(pcfg):
    from momentum.portfolio import build_target_book
    book = build_target_book(_tickers(30), pcfg)
    assert book.n_equity == 30
    assert book.equity_weight == 0.75
    assert book.cash_weight == 0.25
    assert book.weights["BIL"] == 0.25
    assert abs(sum(book.weights.values()) - 1.0) < 1e-9
    assert not book.below_floor


def test_below_floor_lets_cash_grow(pcfg):
    from momentum.portfolio import build_target_book
    book = build_target_book(_tickers(20), pcfg)
    assert book.n_equity == 20
    assert book.cash_weight == 0.5
    assert book.below_floor                     # 20 < 25 floor


def test_oversubscribed_capped_at_n_max(pcfg):
    from momentum.portfolio import build_target_book
    book = build_target_book(_tickers(55), pcfg)
    assert book.n_equity == 40                  # capped
    assert book.cash_weight == 0.0


def test_zero_qualifiers_all_cash(pcfg):
    from momentum.portfolio import build_target_book
    book = build_target_book([], pcfg)
    assert book.n_equity == 0
    assert book.cash_weight == 1.0
    assert book.weights == {"BIL": 1.0}
    assert book.below_floor
