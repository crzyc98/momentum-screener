"""Universe ingestion + liquidity/size floors.

Seed list comes from a Fidelity screener cap-filter export — ``.xls``/``.xlsx``
or CSV (locating the Symbol column, skipping any preamble) — or a plain
one-ticker-per-line list. The engine then re-applies its own >= $20B / price /
liquidity floors as a guardrail, regardless of what the seed list contained.

Fidelity uses ``/`` for share classes (BRK/B); Yahoo/yfinance uses ``-`` (BRK-B),
so symbols are normalized on the way in.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd

_SYMBOL_COL_CANDIDATES = ("symbol", "ticker", "symbols", "ticker symbol")
_TICKER_RE = re.compile(r"^[A-Z][A-Z.\-]{0,9}$")


def normalize_symbol(raw: str) -> str:
    """Fidelity -> Yahoo ticker form: uppercase, share-class '/' becomes '-'."""
    return str(raw).strip().upper().replace("/", "-")


def load_tickers(path: str | Path) -> list[str]:
    """Parse a universe file into a de-duplicated, ordered, Yahoo-form ticker list."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Universe file not found: {path}")

    if path.suffix.lower() in (".xls", ".xlsx"):
        raw = _from_excel(path)
    else:
        text = path.read_text()
        raw = _from_csv(text)
        if raw is None:
            raw = _from_plain_list(text)

    seen: dict[str, None] = {}
    for t in raw:
        t = normalize_symbol(t)
        if t and _TICKER_RE.match(t) and t not in seen:
            seen[t] = None
    return list(seen.keys())


def _symbol_column(df: pd.DataFrame):
    return next(
        (c for c in df.columns if str(c).strip().lower() in _SYMBOL_COL_CANDIDATES),
        None,
    )


def _from_excel(path: Path) -> list[str]:
    """Read the Symbol column from a Fidelity .xls/.xlsx export."""
    engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
    df = pd.read_excel(path, engine=engine)
    col = _symbol_column(df)
    if col is None:
        raise ValueError(f"No Symbol column found in {path} (columns: {list(df.columns)})")
    return [str(v) for v in df[col].dropna().tolist()]


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
        col = _symbol_column(df)
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
