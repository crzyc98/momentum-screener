# Momentum Sleeve Screener

A transparent, **deterministic, auditable** implementation of the Porterhouse-style
monthly momentum sleeve described in [`momentum_sleeve_screener_v1.md`](momentum_sleeve_screener_v1.md).

The funnel:

```
Universe (Fidelity cap-filter export)  →  ≥$20B / price / liquidity floors
        →  Fundamental quality gate  (EPS growth · FCF>0 · OCF≥Net Income · profitability top-half)
        →  Technical/trend gate      (Price > 50-SMA > 200-SMA · within 5% of 52-wk high)
        →  Rank survivors by composite momentum (3/6/9-mo blend, skip ~1 week)
        →  Top-N (≤40) equal-weight 2.5% each  |  remainder → BIL  (the cash accordion)
```

It does three things — **screen**, **reconstitute**, **backtest** — from one CLI, plus a
local Streamlit dashboard.

## Design principles (locked)

- **Deterministic & auditable.** Same `--as-of` date ⇒ byte-identical output. Every name
  that drops is logged with the gate + reason in `audit.csv`. A dated snapshot cache
  (`data/cache/<as_of>/`) means re-runs read the same raw data instead of re-hitting the
  network. Stable sorts with an explicit tie-break (momentum desc, then ticker asc).
- **HALO is observational only in v1.** Heavy-Assets/Low-Obsolescence is computed as a
  *deterministic GICS-sector tag* (`halo` column) — **never** an LLM call. It rides along
  and is reported, but it does **not** gate or reweight anything. This keeps a clean
  pure-momentum+quality baseline so HALO's contribution can be *measured* before it's ever
  promoted to a tie-breaker (v2). A stochastic semantic gate would make the strategy
  non-reproducible — the opposite of the point. See `src/momentum/halo.py`.
- **All dials live in `config/strategy.yaml`.** No magic numbers in code. Tune freely.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## Usage

**Screen** (the monthly buy list + target-weight table):

```bash
.venv/bin/momentum screen \
  --universe data/universe/example_universe.txt \
  --as-of 2025-05-30
```

**Reconstitute** (evaluate current holdings against the §7 sell rules, emit the
add/delete/retain diff + an optional Smart-Buy allocation of new cash):

```bash
.venv/bin/momentum reconstitute \
  --universe data/universe/example_universe.txt \
  --holdings data/holdings/example_holdings.csv \
  --as-of 2025-05-30 \
  --contribution 10000
```

**Backtest** (monthly walk-forward vs SPY):

```bash
.venv/bin/momentum backtest \
  --universe data/universe/example_universe.txt \
  --start 2022-01-01 --end 2024-12-31
```

**Dashboard:**

```bash
.venv/bin/streamlit run app/dashboard.py
```

All runs write a self-contained record under `data/out/<as_of>/`
(`report.md`, `target_weights.csv`, `selected.csv`, `audit.csv`, `summary.json`;
reconstitution adds `reconstitution.md`, `holdings_eval.csv`, `rebalance.json`).

## Inputs

- **Universe** — a Fidelity Stock Screener cap-filter CSV export (the engine finds the
  `Symbol` column and skips any preamble) **or** a plain one-ticker-per-line list. The
  engine then re-applies its own ≥$20B / price / liquidity floors regardless.
- **Holdings** — a Fidelity basket export (or simple `Symbol,Weight,Current Value` CSV).
  Smart-Buy needs the value column.

## Data source & known limitations

Data comes from **yfinance** (free) behind a swappable `DataProvider` protocol
(`src/momentum/providers/`). Be aware of three honest limitations:

1. **Fundamentals are current-snapshot only.** yfinance exposes today's `marketCap`,
   `operatingCashflow`, `trailingEps`, etc. — not point-in-time history. For a live monthly
   screen this is fine. For backtests it isn't (see below).
2. **Forward EPS coverage is spotty.** Forward EPS growth is a proxy
   `(forwardEps − trailingEps)/|trailingEps|`. Missing data is handled by
   `missing_data_policy` (default `skip` — don't penalize a yfinance gap; set `fail` for strict).
3. **No S&P Global quality score.** The "quality top half" gate uses a momentum-neutral
   profitability proxy (Novy-Marx / QMJ style): mean z-score of **ROA, gross margin, and
   operating margin** over the liquidity-passed universe. The Fidelity field map uses the real
   S&P Global score directly.

### Why the fundamental gate is quality, not value (v1.1)

"Strong cash flows" means cash **generation + accruals quality**, not cheapness. An earlier
draft used **P/CF top-quartile** — a *value* gate. Value and momentum are negatively correlated
(Asness/Moskowitz/Pedersen), so stapling a value gate onto a momentum screen collapses the book
(live test: ~4 names / 90% cash). v1.1 measures cash quality instead: **FCF > 0**, **OCF ≥ Net
Income** (Sloan accruals — the correct "harder to manipulate than GAAP earnings" check), and a
**top-half profitability** score. P/CF survives only as an optional **sanity ceiling**
(`pcf_ceiling`, default 60) to drop blow-off multiples — never a top-quartile requirement.
A future refinement (FCF margin rising YoY) needs the statements feed and is **not yet wired**.

### Backtest caveats (stamped into `backtest.md`)

- **`--fundamentals skip` is the faithful default**: it runs only the price-based gates
  (SMAs, golden cross, 52-wk high, composite momentum), which *do* backtest correctly from
  historical OHLCV. `--fundamentals approx` applies today's fundamentals at every past
  month-end — **look-ahead biased**, labeled as such.
- A fixed current universe list carries **survivorship bias**.
- The snapshot cache accumulates real point-in-time fundamentals from first run forward, so
  live-tracked backtests improve over time.

## Project layout

```
config/strategy.yaml      all dials (universe, gates, momentum, accordion, sell, halo, backtest)
src/momentum/
  config.py               typed/validated config
  providers/              DataProvider protocol + yfinance impl (snapshot cache)
  universe.py holdings.py  input parsing
  indicators.py           pure SMA / RSI / momentum / 52-wk-high
  gates.py                liquidity, fundamental (cross-sectional), technical
  halo.py                 deterministic observational HALO tag
  screener.py             funnel orchestration + audit trail
  portfolio.py            equal weight + cash accordion
  sell_discipline.py      §7 exit triggers
  reconstitution.py       diff + Smart-Buy
  report.py               markdown/CSV/JSON artifacts
  backtest.py             monthly walk-forward vs benchmark
  cli.py                  screen | reconstitute | backtest
app/dashboard.py          Streamlit UI (Screen / Holdings / Rebalance / Backtest)
tests/                    indicators, gates, accordion, determinism, HALO-non-gating, I/O, smart-buy
```

## Tests

```bash
.venv/bin/python -m pytest -q
```

## Not investment advice

A rules-based tool, not advice. Absolute-momentum strategies trade whipsaw risk for crash
protection — expect to be occasionally sold out of a name that recovers, and occasionally
sitting in T-bills during a violent bottom. That's the deal.
