"""Parse a current-holdings CSV (Fidelity basket export or simple ticker/weight/value).

Tolerates Fidelity preamble rows and maps common column aliases. Returns a tidy
frame with columns: ticker, weight (fraction or NaN), value (USD or NaN).
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

_SYMBOL_ALIASES = ("symbol", "ticker")
_WEIGHT_ALIASES = ("weight", "target weight", "current weight", "% of account", "allocation")
_VALUE_ALIASES = ("value", "current value", "market value", "current value ($)", "mkt value")


def _find(cols, aliases):
    lower = {str(c).strip().lower(): c for c in cols}
    for a in aliases:
        if a in lower:
            return lower[a]
    return None


def _to_fraction(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace("%", "", regex=False).str.replace(",", "", regex=False)
    nums = pd.to_numeric(s, errors="coerce")
    # If values look like percentages (e.g., 2.5 not 0.025), scale down.
    if nums.dropna().abs().max() is not None and nums.dropna().abs().max() > 1.5:
        nums = nums / 100.0
    return nums


def _to_money(series: pd.Series) -> pd.Series:
    s = (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    return pd.to_numeric(s, errors="coerce")


def load_holdings(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Holdings file not found: {path}")
    lines = path.read_text().splitlines()

    df = None
    for skip in range(min(10, len(lines))):
        try:
            cand = pd.read_csv(io.StringIO("\n".join(lines[skip:])))
        except Exception:
            continue
        if not cand.empty and _find(cand.columns, _SYMBOL_ALIASES):
            df = cand
            break
    if df is None:
        raise ValueError(f"Could not locate a Symbol column in {path}")

    sym = _find(df.columns, _SYMBOL_ALIASES)
    wcol = _find(df.columns, _WEIGHT_ALIASES)
    vcol = _find(df.columns, _VALUE_ALIASES)

    out = pd.DataFrame({"ticker": df[sym].astype(str).str.strip().str.upper()})
    out["weight"] = _to_fraction(df[wcol]) if wcol else pd.NA
    out["value"] = _to_money(df[vcol]) if vcol else pd.NA
    out = out[out["ticker"].str.match(r"^[A-Z][A-Z.\-]{0,9}$", na=False)]
    return out.reset_index(drop=True)
