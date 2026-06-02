"""Portfolio construction: equal weights + the T-bill cash accordion.

The accordion is the absolute-momentum mechanism: you never pad the book with
marginal names to stay fully invested. Fewer qualifiers => more T-bills,
automatically.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from momentum.config import PortfolioConfig


@dataclass
class TargetBook:
    weights: dict[str, float]       # ticker -> target weight (sums to ~1.0)
    n_equity: int
    equity_weight: float
    cash_weight: float
    cash_ticker: str
    below_floor: bool               # fewer than min_names_floor qualified

    def to_frame(self) -> pd.DataFrame:
        rows = [{"ticker": t, "weight": w} for t, w in self.weights.items()]
        return pd.DataFrame(rows)


def build_target_book(selected_tickers: list[str], cfg: PortfolioConfig) -> TargetBook:
    """Assign 2.5% per selected name; route the remainder to the cash sleeve.

    Order of ``selected_tickers`` is preserved (caller passes momentum rank order).
    """
    n = min(len(selected_tickers), cfg.n_max)
    chosen = selected_tickers[:n]
    w = cfg.weight_per_name

    weights: dict[str, float] = {t: w for t in chosen}
    equity_weight = round(n * w, 10)
    cash_weight = round(1.0 - equity_weight, 10)
    if cash_weight < 0:  # only possible if weight_per_name * n_max > 1
        cash_weight = 0.0
    if cash_weight > 0:
        weights[cfg.cash_ticker] = cash_weight

    return TargetBook(
        weights=weights,
        n_equity=n,
        equity_weight=equity_weight,
        cash_weight=cash_weight,
        cash_ticker=cfg.cash_ticker,
        below_floor=n < cfg.min_names_floor,
    )
