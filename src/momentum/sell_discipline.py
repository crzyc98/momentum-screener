"""Monthly sell discipline (§7): exit != inverse of entry.

A held name is excised at month-end if ANY trigger fires:
  - price closes meaningfully (> buffer) below its 50-day SMA, or
  - it fell out of the top-N composite-momentum rank, or
  - it dropped off the screener entirely (failed a fundamental/technical gate), or
  - sustained relative-strength breakdown vs the benchmark.

Returns one row per holding tagged HOLD/SELL with the specific reason(s).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from momentum import indicators as ind
from momentum.config import Config
from momentum.providers.base import DataProvider
from momentum.screener import ScreenResult


def _relative_strength(
    provider: DataProvider, ticker: str, as_of: date, lookback: int
) -> float | None:
    """Holding return minus benchmark return over the lookback window."""
    h = provider.price_history(ticker, as_of)
    if h.empty or "Close" not in h:
        return None
    hr = ind.total_return(h["Close"].astype(float), lookback, skip_days=0)
    return hr


def evaluate_holdings(
    provider: DataProvider,
    holdings: pd.DataFrame,
    result: ScreenResult,
    cfg: Config,
    as_of: date,
) -> pd.DataFrame:
    """Tag every current holding HOLD or SELL with reasons, per §7."""
    selected = set(result.selected["ticker"]) if not result.selected.empty else set()
    qualified = set(result.survivors["ticker"]) if not result.survivors.empty else set()

    # Benchmark return over the RS window (computed once).
    lb = cfg.sell.rs_breakdown_lookback_days
    bench = provider.price_history(cfg.backtest.benchmark, as_of)
    bench_ret = (
        ind.total_return(bench["Close"].astype(float), lb, 0)
        if not bench.empty and "Close" in bench
        else None
    )

    rows: list[dict] = []
    for tkr in holdings["ticker"]:
        if tkr == cfg.portfolio.cash_ticker:
            continue  # the cash sleeve is managed by the accordion, not sold
        prices = provider.price_history(tkr, as_of)
        reasons: list[str] = []

        if prices.empty or "Close" not in prices:
            reasons.append("no price data")
        else:
            close = prices["Close"].astype(float)
            price = float(close.iloc[-1])
            sma50 = ind.sma(close, 50)
            if sma50 is not None and price < sma50 * (1 - cfg.sell.sma50_buffer_pct):
                reasons.append(
                    f"price {price:.2f} > {cfg.sell.sma50_buffer_pct:.0%} below 50-SMA {sma50:.2f}"
                )
            # Relative-strength breakdown vs benchmark.
            if bench_ret is not None:
                hr = ind.total_return(close, lb, 0)
                if hr is not None and (hr - bench_ret) < cfg.sell.rs_breakdown_threshold:
                    reasons.append(
                        f"RS breakdown: {hr-bench_ret:+.1%} vs {cfg.backtest.benchmark} "
                        f"over {lb}d (< {cfg.sell.rs_breakdown_threshold:+.0%})"
                    )

        if cfg.sell.drop_if_off_screener and tkr not in qualified:
            reasons.append("dropped off screener (failed a gate)")
        elif cfg.sell.drop_if_out_of_top_n and tkr not in selected:
            # qualified but outside top-N
            reasons.append("fell out of top-N momentum rank")

        rows.append({
            "ticker": tkr,
            "action": "SELL" if reasons else "HOLD",
            "reasons": "; ".join(reasons),
            "in_top_n": tkr in selected,
            "qualified": tkr in qualified,
        })

    return pd.DataFrame(rows)
