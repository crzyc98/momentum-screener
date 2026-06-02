# Monthly Paper-Trade Runbook

Paper-trade the sleeve to (1) validate the *operational* flow — does the monthly ritual
actually work, how does reconstitution/Smart-Buy feel — and (2) **bank a clean point-in-time
snapshot every month**. That forward PIT record is the real prize: it's the only
contamination-free data we can later backtest on (yfinance's history is restated +
survivorship-biased — see `DESIGN_pit_backtest.md`).

> Paper trading tests **execution**. The backtest tests **strategy logic across regimes**.
> Neither substitutes for the other. One paper month is noise on returns — its value is the
> banked snapshot + the process check. Don't read P&L into a single month.

**Cadence:** last trading day of each month. ~10 minutes.

---

## The ritual

### 1. Export a fresh universe from Fidelity
Run the Fidelity Stock Screener with **just the cap floor** (Market Cap ≥ $20B) — the engine
does the rest. **Export → `screener_results.xls`** in the repo root (overwrite last month's).
*(Re-exporting monthly matters: it's how new large-caps enter and fallen ones leave — keeping
the universe honest, though note it does NOT fix historical survivorship for backtests.)*

### 2. Run the screen for this month-end
```bash
.venv/bin/momentum screen --universe screener_results.xls --as-of YYYY-MM-DD
```
This writes `data/out/<as_of>/` (report.md, target_weights.csv, selected.csv, audit.csv) **and**
banks the PIT snapshot in `data/cache/<as_of>/` — **do not delete that folder.**

Eyeball the report: qualified count, equity/cash split, and the **`Unverified qual.`** line —
any name flagged `quality_unverified` cleared the quality floor only on a missing field; decide
case-by-case whether to keep it.

### 3. Reconstitute against the current paper book
```bash
.venv/bin/momentum reconstitute \
  --universe screener_results.xls \
  --holdings data/holdings/paper_<prev_as_of>.csv \
  --as-of YYYY-MM-DD \
  --contribution 0     # set to your monthly deposit to exercise Smart-Buy
```
Read `data/out/<as_of>/reconstitution.md`:
- **Sell-discipline (§7):** which holdings tripped SELL and why.
- **Diff:** adds / deletes / retains.
- **Smart-Buy:** if you passed a contribution, where the new cash routes (underweights only).

### 4. Roll the paper book forward
The new month's target book becomes next month's paper holdings. Generate it from this run's
target weights at your running portfolio value (start $100k; bump by your contribution and,
if you want true P&L, mark-to-market — a v2 refinement):
```bash
.venv/bin/python - <<'PY'
import pandas as pd
AS_OF, CAP = "YYYY-MM-DD", 100_000.0     # CAP = prior value + contribution (+ MTM later)
tw = pd.read_csv(f"data/out/{AS_OF}/target_weights.csv")
pd.DataFrame({
    "Symbol": tw["ticker"],
    "Weight": (tw["weight"]*100).map(lambda v: f"{v:.2f}%"),
    "Current Value": (tw["weight"]*CAP).round(2),
}).to_csv(f"data/holdings/paper_{AS_OF}.csv", index=False)
print("rolled ->", f"data/holdings/paper_{AS_OF}.csv")
PY
```

### 5. Record the month
Keep `data/out/<as_of>/` and `data/cache/<as_of>/` (commit them or back them up). The cache
folder is the banked point-in-time fundamentals — your future backtest's clean data.

---

## What to watch over the first few months
- **Process:** does reconstitution feel like ~10 min / one block? Where's the friction?
- **Turnover & cash:** is the accordion expanding/contracting sensibly with the tape?
- **`quality_unverified` names:** recurring offenders (e.g. financials with no FCF in yfinance)
  may warrant a per-name override or a `fail`-policy carve-out.
- **HALO column:** how much heavy-asset tilt would a v2 overlay impose vs. the natural book?

## Current state
- Starting paper book: `data/holdings/paper_2026-05-29.csv` (31 names + BIL, $100k).
- First banked snapshot: `data/cache/2026-05-29/`.
- **Do not** automate this yet — run it by hand until you trust it (automation is a v2 reward).
