"""Reporting: the Claude-style target-weight markdown table, plus CSV/JSON
artifacts and the gate audit log.

Everything is written under ``data/out/<as_of>/`` so each month's run is a
self-contained, reviewable record.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from momentum.portfolio import TargetBook
from momentum.screener import ScreenResult

# Columns surfaced in the human-readable survivor/selected views.
_DISPLAY_COLS = [
    "rank", "ticker", "sector", "halo", "momentum",
    "pct_off_high", "rsi", "pcf", "quality_score", "market_cap",
]


def target_weight_table(book: TargetBook, selected: pd.DataFrame) -> str:
    """Markdown table of ticker -> target weight, ready to type into Fidelity."""
    lines = ["| Ticker | Target Weight | Sector | HALO |", "|---|---|---|---|"]
    meta = selected.set_index("ticker") if not selected.empty else pd.DataFrame()
    for tkr, wt in book.weights.items():
        if tkr == book.cash_ticker and tkr not in meta.index:
            sector, halo = "Cash (T-bill)", ""
        else:
            sector = str(meta.loc[tkr, "sector"]) if tkr in meta.index else ""
            halo = "✓" if (tkr in meta.index and bool(meta.loc[tkr, "halo"])) else ""
        lines.append(f"| {tkr} | {wt:.2%} | {sector} | {halo} |")
    return "\n".join(lines)


def summary_text(result: ScreenResult, book: TargetBook) -> str:
    floor_note = (
        f"\n⚠️  Only {book.n_equity} names qualified — below the {book.cash_weight:.0%} "
        "min-names floor; cash is allowed to grow rather than forcing exposure."
        if book.below_floor else ""
    )
    halo_n = int(result.selected["halo"].sum()) if not result.selected.empty else 0
    return (
        f"Momentum Sleeve — screen as of {result.as_of.isoformat()}\n"
        f"  Universe scanned : {len(result.audit)}\n"
        f"  Qualified        : {len(result.survivors)}\n"
        f"  Selected (top-N) : {book.n_equity}  "
        f"(equity {book.equity_weight:.1%} / cash {book.cash_weight:.1%} in {book.cash_ticker})\n"
        f"  HALO in book     : {halo_n}/{book.n_equity}  (observational only — not gating)"
        f"{floor_note}"
    )


def write_artifacts(
    result: ScreenResult, book: TargetBook, out_dir: str | Path
) -> Path:
    """Write the full month-end record; returns the output directory."""
    out = Path(out_dir) / result.as_of.isoformat()
    out.mkdir(parents=True, exist_ok=True)

    # Audit trail — every input ticker, stage, reason, metrics.
    result.audit.to_csv(out / "audit.csv", index=False)

    # Selected book + weights.
    book.to_frame().to_csv(out / "target_weights.csv", index=False)
    avail = [c for c in _DISPLAY_COLS if c in result.selected.columns]
    result.selected[avail].to_csv(out / "selected.csv", index=False)

    # Markdown report.
    md = (
        f"# Momentum Sleeve — {result.as_of.isoformat()}\n\n"
        f"```\n{summary_text(result, book)}\n```\n\n"
        f"## Target weights\n\n{target_weight_table(book, result.selected)}\n"
    )
    (out / "report.md").write_text(md)

    # Machine-readable summary.
    (out / "summary.json").write_text(json.dumps({
        "as_of": result.as_of.isoformat(),
        "universe_scanned": len(result.audit),
        "qualified": len(result.survivors),
        "selected": book.n_equity,
        "equity_weight": book.equity_weight,
        "cash_weight": book.cash_weight,
        "cash_ticker": book.cash_ticker,
        "below_floor": book.below_floor,
        "weights": book.weights,
    }, indent=2))

    return out


def drop_breakdown(result: ScreenResult) -> pd.Series:
    """Count of names dropped at each funnel stage (for quick diagnostics)."""
    return result.audit["stage"].value_counts()
