"""Universe ingestion + liquidity/size floors.

Seed list comes from a Fidelity screener cap-filter CSV export (preferred) or a
plain one-ticker-per-line text/CSV file. The engine then re-applies its own
>= $20B / price / liquidity floors as a guardrail, regardless of what the seed
list contained.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd

_SYMBOL_COL_CANDIDATES = ("symbol", "ticker", "symbols", "ticker symbol")
_TICKER_RE = re.compile(r"^[A-Z][A-Z.\-]{0,9}$")


def load_tickers(path: str | Path) -> list[str]:
    """Parse a universe file into a de-duplicated, ordered ticker list.

    Handles Fidelity CSV exports (locating the Symbol column, skipping any
    preamble) and plain newline-delimited lists.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Universe file not found: {path}")
    text = path.read_text()

    tickers = _from_csv(text)
    if tickers is None:
        tickers = _from_plain_list(text)

    seen: dict[str, None] = {}
    for t in tickers:
        t = t.strip().upper()
        if t and _TICKER_RE.match(t) and t not in seen:
            seen[t] = None
    return list(seen.keys())


def _from_csv(text: str) -> list[str] | None:
    """Try to read a Symbol column out of a (possibly preamble-prefixed) CSV."""
    lines = text.splitlines()
    for skip in range(min(10, len(lines))):  # tolerate Fidelity preamble rows
        try:
            df = pd.read_csv(io.StringIO("\n".join(lines[skip:])))
        except Exception:
            continue
        if df.empty:
            continue
        col = next(
            (c for c in df.columns if str(c).strip().lower() in _SYMBOL_COL_CANDIDATES),
            None,
        )
        if col is not None:
            return [str(v) for v in df[col].dropna().tolist()]
    return None


def _from_plain_list(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        token = line.split(",")[0].strip()
        if token and not token.lower().startswith(("symbol", "ticker")):
            out.append(token)
    return out
