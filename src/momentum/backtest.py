"""Monthly walk-forward backtester.

Honest about its limits (governance matters here):

  * **Price-based gates** (50/200 SMA, golden cross, 52-wk high, composite
    momentum) backtest faithfully from historical OHLCV.
  * **Fundamental gate canNOT be point-in-time with yfinance** — only *current*
    fundamentals exist. So the backtest defaults to ``fundamentals="skip"``
    (technical+momentum only, clearly labeled). ``fundamentals="approx"`` applies
    today's fundamentals at every past month-end, which is look-ahead-biased and
    labeled as such in the output.
  * The universe is whatever you pass in; a fixed current list carries
    **survivorship bias**. Both caveats are stamped into ``backtest.md``.

Determinism: each ticker's full history is loaded once, then sliced per month —
no per-month network calls, identical results on re-run from cache.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from momentum.config import Config
from momentum.portfolio import build_target_book
from momentum.providers.base import DataProvider
from momentum.screener import run_screen
from momentum.universe import load_tickers

TRADING_DAYS_PER_YEAR = 252


class _SeriesProvider:
    """In-memory DataProvider over pre-loaded full histories (slices per as_of)."""

    def __init__(self, prices: dict[str, pd.DataFrame], info: dict[str, dict]):
        self._prices = prices
        self._info = info

    def price_history(self, ticker: str, as_of: date) -> pd.DataFrame:
        df = self._prices.get(ticker)
        if df is None or df.empty:
            return pd.DataFrame()
        return df[df.index.date <= as_of]

    def info(self, ticker: str, as_of: date) -> dict:
        return self._info.get(ticker, {})


def _price_asof(series: pd.Series, when: pd.Timestamp) -> float | None:
    s = series[series.index <= when]
    return float(s.iloc[-1]) if len(s) else None


def _preload(provider: DataProvider, tickers: list[str], end: date) -> _SeriesProvider:
    prices, info = {}, {}
    for t in tickers:
        prices[t] = provider.price_history(t, end)
        info[t] = provider.info(t, end)
    return _SeriesProvider(prices, info)


def _metrics(returns: pd.Series, equity: pd.Series) -> dict:
    if returns.empty:
        return {}
    n_years = max(len(returns) / 12.0, 1e-9)
    total = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1 / n_years) - 1.0)
    vol = float(returns.std(ddof=0) * np.sqrt(12))
    sharpe = float((returns.mean() * 12) / vol) if vol > 0 else 0.0
    roll_max = equity.cummax()
    max_dd = float((equity / roll_max - 1.0).min())
    hit = float((returns > 0).mean())
    return {
        "total_return": total, "cagr": cagr, "ann_vol": vol,
        "sharpe": sharpe, "max_drawdown": max_dd, "hit_rate": hit,
    }


def run_backtest(
    provider: DataProvider, cfg: Config, universe_path: str,
    start: str, end: str, fundamentals: str = "skip",
) -> dict:
    tickers = load_tickers(universe_path)
    start_d, end_d = pd.Timestamp(start).date(), pd.Timestamp(end).date()
    cash = cfg.portfolio.cash_ticker
    bench = cfg.backtest.benchmark

    print(f"Backtest {start} -> {end} | universe {len(tickers)} | "
          f"fundamentals={fundamentals}")
    # Ensure preload covers from before `start` (200-day SMA + 9-mo momentum warmup).
    needed_years = int((end_d - start_d).days / 365.25) + 2
    if hasattr(provider, "history_years"):
        provider.history_years = max(getattr(provider, "history_years", 0), needed_years)
    sp = _preload(provider, [*tickers, cash, bench], end_d)

    # Screen config: faithfully drop the un-backtestable fundamental gate by default.
    scfg = deepcopy(cfg)
    if fundamentals == "skip":
        scfg.fundamental.require_positive_trailing_eps_growth = False
        scfg.fundamental.require_positive_forward_eps_growth = False
        scfg.fundamental.pcf_top_quartile = False
        scfg.fundamental.quality_top_tier = False

    rebal_dates = pd.date_range(start=start, end=end, freq="BME")  # business month-end
    cash_series = sp._prices.get(cash, pd.DataFrame()).get("Close")
    bench_series = sp._prices.get(bench, pd.DataFrame()).get("Close")

    records: list[dict] = []
    prev_weights: dict[str, float] = {}
    for i in range(len(rebal_dates) - 1):
        m, nxt = rebal_dates[i], rebal_dates[i + 1]
        result = run_screen(sp, tickers, m.date(), scfg)
        book = build_target_book(result.selected["ticker"].tolist(), cfg.portfolio)

        # Portfolio return from m -> nxt using fixed target weights.
        port_ret = 0.0
        for tkr, w in book.weights.items():
            series = (cash_series if tkr == cash else sp._prices.get(tkr, pd.DataFrame()).get("Close"))
            if series is None or series.empty:
                # Missing cash ETF history (e.g. pre-inception) -> treat as flat.
                continue
            p0, p1 = _price_asof(series, m), _price_asof(series, nxt)
            if p0 and p1 and p0 > 0:
                port_ret += w * (p1 / p0 - 1.0)

        bench_ret = 0.0
        if bench_series is not None and not bench_series.empty:
            b0, b1 = _price_asof(bench_series, m), _price_asof(bench_series, nxt)
            if b0 and b1 and b0 > 0:
                bench_ret = b1 / b0 - 1.0

        turnover = 0.5 * sum(
            abs(book.weights.get(t, 0.0) - prev_weights.get(t, 0.0))
            for t in set(book.weights) | set(prev_weights)
        )
        prev_weights = book.weights

        records.append({
            "date": nxt.date().isoformat(),
            "port_ret": port_ret, "bench_ret": bench_ret,
            "n_equity": book.n_equity, "cash_weight": book.cash_weight,
            "turnover": turnover,
        })

    if not records:
        print("No rebalance periods in range.")
        return {}

    hist = pd.DataFrame(records).set_index("date")
    cap = cfg.backtest.initial_capital
    hist["equity"] = cap * (1 + hist["port_ret"]).cumprod()
    hist["bench_equity"] = cap * (1 + hist["bench_ret"]).cumprod()

    port_m = _metrics(hist["port_ret"], hist["equity"])
    bench_m = _metrics(hist["bench_ret"], hist["bench_equity"])
    extra = {
        "avg_n_equity": float(hist["n_equity"].mean()),
        "avg_cash_weight": float(hist["cash_weight"].mean()),
        "avg_turnover": float(hist["turnover"].iloc[1:].mean()) if len(hist) > 1 else 0.0,
        "win_vs_bench": float((hist["port_ret"] > hist["bench_ret"]).mean()),
        "months": len(hist),
        "fundamentals_mode": fundamentals,
    }

    out = _write(cfg, hist, port_m, bench_m, extra, start, end)
    _print_summary(port_m, bench_m, extra)
    print(f"\nArtifacts written to: {out}")
    return {"strategy": port_m, "benchmark": bench_m, "extra": extra}


def _write(cfg, hist, port_m, bench_m, extra, start, end) -> Path:
    out = Path(cfg.data.out_dir) / "backtest"
    out.mkdir(parents=True, exist_ok=True)
    hist.to_csv(out / "equity_curve.csv")
    (out / "metrics.json").write_text(json.dumps(
        {"strategy": port_m, "benchmark": bench_m, "extra": extra}, indent=2))

    caveat = (
        "> **Caveats:** "
        + ("Fundamental gate SKIPPED (price-based gates only) — the faithful default, "
           "since yfinance has no point-in-time fundamentals. "
           if extra["fundamentals_mode"] == "skip" else
           "Fundamental gate uses TODAY's fundamentals at every past month-end "
           "(look-ahead bias — interpret with caution). ")
        + "Universe is a fixed current list (survivorship bias)."
    )
    rows = "\n".join(
        f"| {k} | {port_m.get(k, float('nan')):.2%} | {bench_m.get(k, float('nan')):.2%} |"
        for k in ("total_return", "cagr", "ann_vol", "max_drawdown", "hit_rate")
    )
    md = (
        f"# Backtest {start} → {end}\n\n{caveat}\n\n"
        f"| Metric | Strategy | {cfg.backtest.benchmark} |\n|---|---|---|\n{rows}\n"
        f"| sharpe | {port_m['sharpe']:.2f} | {bench_m['sharpe']:.2f} |\n\n"
        f"- Avg equity names: {extra['avg_n_equity']:.1f}\n"
        f"- Avg cash weight (time-in-cash): {extra['avg_cash_weight']:.1%}\n"
        f"- Avg monthly turnover: {extra['avg_turnover']:.1%}\n"
        f"- Months outperforming {cfg.backtest.benchmark}: {extra['win_vs_bench']:.1%}\n"
    )
    (out / "backtest.md").write_text(md)
    return out


def _print_summary(port_m, bench_m, extra):
    print(f"\n  Strategy CAGR {port_m['cagr']:.2%} | vol {port_m['ann_vol']:.2%} | "
          f"Sharpe {port_m['sharpe']:.2f} | maxDD {port_m['max_drawdown']:.2%}")
    print(f"  {('Benchmark'):8} CAGR {bench_m['cagr']:.2%} | vol {bench_m['ann_vol']:.2%} | "
          f"Sharpe {bench_m['sharpe']:.2f} | maxDD {bench_m['max_drawdown']:.2%}")
    print(f"  Avg names {extra['avg_n_equity']:.1f} | avg cash {extra['avg_cash_weight']:.1%} | "
          f"turnover {extra['avg_turnover']:.1%} | win-vs-bench {extra['win_vs_bench']:.1%}")
