"""Monthly reconstitution: diff held vs new book, plus the Smart-Buy allocator.

Smart-Buy routes a new cash contribution exclusively into the most underweight
names (never forcing a taxable sale), per the doc's tax-efficiency mechanic. A
full rebalance (the target weights) is always emitted too.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from momentum.config import Config
from momentum.holdings import load_holdings
from momentum.portfolio import TargetBook, build_target_book
from momentum.report import summary_text, write_artifacts
from momentum.screener import run_screen
from momentum.sell_discipline import evaluate_holdings
from momentum.universe import load_tickers


@dataclass
class RebalancePlan:
    as_of: date
    book: TargetBook
    holdings_eval: pd.DataFrame      # HOLD/SELL per current holding
    adds: list[str]                  # in new book, not currently held
    deletes: list[str]               # held, not in new book
    retained: list[str]              # in both
    smart_buy: dict[str, float] = field(default_factory=dict)  # ticker -> $ to buy
    contribution: float = 0.0


def smart_buy_allocation(
    book: TargetBook, holdings: pd.DataFrame, contribution: float
) -> dict[str, float]:
    """Allocate ``contribution`` to underweights only (no sells).

    Needs per-holding dollar values. Returns {} if values or contribution absent.
    """
    if contribution <= 0 or holdings["value"].isna().all():
        return {}
    cur_val = (
        holdings.dropna(subset=["value"])
        .groupby("ticker")["value"]
        .sum()
        .to_dict()
    )
    v_old = sum(cur_val.values())
    v_new = v_old + contribution
    gaps: dict[str, float] = {}
    for tkr, w in book.weights.items():
        target_value = w * v_new
        gap = target_value - cur_val.get(tkr, 0.0)
        if gap > 0:
            gaps[tkr] = gap
    total_gap = sum(gaps.values())
    if total_gap <= 0:
        return {}
    if total_gap <= contribution:
        alloc = dict(gaps)  # fully fill underweights
        leftover = contribution - total_gap
        if leftover > 0:  # park remainder in the cash sleeve
            alloc[book.cash_ticker] = alloc.get(book.cash_ticker, 0.0) + leftover
    else:  # ration the contribution proportionally to the gaps
        alloc = {t: contribution * (g / total_gap) for t, g in gaps.items()}
    return {t: round(v, 2) for t, v in alloc.items()}


def build_plan(
    provider, cfg: Config, as_of: date, tickers: list[str],
    holdings: pd.DataFrame, contribution: float,
):
    result = run_screen(provider, tickers, as_of, cfg)
    book = build_target_book(result.selected["ticker"].tolist(), cfg.portfolio)
    holdings_eval = evaluate_holdings(provider, holdings, result, cfg, as_of)

    cash = cfg.portfolio.cash_ticker
    held = {t for t in holdings["ticker"] if t != cash}
    target = {t for t in book.weights if t != cash}
    adds = sorted(target - held)
    deletes = sorted(held - target)
    retained = sorted(held & target)

    plan = RebalancePlan(
        as_of=as_of, book=book, holdings_eval=holdings_eval,
        adds=adds, deletes=deletes, retained=retained,
        smart_buy=smart_buy_allocation(book, holdings, contribution),
        contribution=contribution,
    )
    return result, plan


def write_plan(result, plan: RebalancePlan, cfg: Config) -> Path:
    out = write_artifacts(result, plan.book, cfg.data.out_dir)
    plan.holdings_eval.to_csv(out / "holdings_eval.csv", index=False)

    lines = [
        f"# Reconstitution — {plan.as_of.isoformat()}", "",
        "## Sell-discipline review (§7)", "",
        plan.holdings_eval.to_markdown(index=False) if not plan.holdings_eval.empty
        else "_No current holdings provided._", "",
        "## Reconstitution diff", "",
        f"- **Add** ({len(plan.adds)}): {', '.join(plan.adds) or '—'}",
        f"- **Delete** ({len(plan.deletes)}): {', '.join(plan.deletes) or '—'}",
        f"- **Retain** ({len(plan.retained)}): {', '.join(plan.retained) or '—'}", "",
    ]
    if plan.smart_buy:
        lines += [
            f"## Smart-Buy allocation of ${plan.contribution:,.0f} (underweights only)", "",
            "| Ticker | Buy $ |", "|---|---|",
            *[f"| {t} | ${v:,.2f} |" for t, v in plan.smart_buy.items()], "",
        ]
    (out / "reconstitution.md").write_text("\n".join(lines))
    (out / "rebalance.json").write_text(json.dumps({
        "as_of": plan.as_of.isoformat(),
        "adds": plan.adds, "deletes": plan.deletes, "retained": plan.retained,
        "target_weights": plan.book.weights,
        "smart_buy": plan.smart_buy, "contribution": plan.contribution,
    }, indent=2))
    return out


def run_reconstitution(
    provider, cfg: Config, as_of: date,
    universe_path: str, holdings_path: str, contribution: float = 0.0,
) -> RebalancePlan:
    tickers = load_tickers(universe_path)
    holdings = load_holdings(holdings_path)
    print(f"Loaded {len(tickers)} universe tickers, {len(holdings)} holdings")
    print(f"Reconstituting as of {as_of.isoformat()} ...")

    result, plan = build_plan(provider, cfg, as_of, tickers, holdings, contribution)
    out = write_plan(result, plan, cfg)

    print("\n" + summary_text(result, plan.book))
    ev = plan.holdings_eval
    sells = ev[ev["action"] == "SELL"] if not ev.empty else pd.DataFrame()
    warned = (
        int((ev["warnings"].fillna("").str.len() > 0).sum())
        if not ev.empty and "warnings" in ev else 0
    )
    print(f"\nSell discipline: {len(sells)} SELL / {len(ev) - len(sells)} HOLD"
          + (f"  ({warned} held with warnings)" if warned else ""))
    print(f"Diff: +{len(plan.adds)} add / -{len(plan.deletes)} delete / "
          f"{len(plan.retained)} retain")
    if plan.smart_buy:
        print(f"Smart-Buy: allocated ${plan.contribution:,.0f} across "
              f"{len(plan.smart_buy)} underweights")
    print(f"\nArtifacts written to: {out}")
    return plan
