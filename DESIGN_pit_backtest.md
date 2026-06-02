# Design: Point-in-Time Backtest (survivorship- & look-ahead-free)

**Status:** spec only — not built. Writing it needs no new data; *building* it needs a paid
point-in-time data feed (yfinance cannot do this). See "Data sources" for cost.

## What this answers (and what it doesn't)

A faithful backtest tests **strategy logic across regimes**: does the rule set hold through a
drawdown, does the cash accordion actually de-risk when leadership narrows, what's the realistic
whipsaw. It does **not** test execution friction (slippage, FIFO, basket mechanics, "does the
ritual take 10 min") — that's what paper trading (`RUNBOOK.md`) is for. Neither substitutes for
the other; run both. Even done perfectly, a backtest of a momentum strategy flatters returns, so
treat output as **directional, not an expected-return estimate.**

## Why the current yfinance backtest is biased

`src/momentum/backtest.py` is honest about this (caveats stamped into `backtest.md`), but to be
explicit, two structural biases both inflate momentum results:

1. **Survivorship.** yfinance only carries *currently listed* tickers. Every company that blew up
   and delisted is silently absent, so the historical universe is pre-cleaned of disasters — the
   exact tail a trend-following sell discipline is supposed to dodge. This affects **both**
   `--fundamentals skip` and `approx` modes.
2. **Look-ahead / restatement.** yfinance fundamentals are *current* values. `--fundamentals
   approx` applies today's (often *restated*) FCF / net income / EPS to past month-ends, when you
   wouldn't have had them — or would have had the *originally reported* number. The accruals
   (OCF≥NI) and FCF gates are especially exposed, since those line items get restated. (Default
   `skip` avoids this by running price-only, but then it isn't testing the fundamental gate at
   all.)

## Requirements for a faithful backtest

| # | Requirement | Why |
|---|---|---|
| R1 | **Point-in-time fundamentals** — values *as first reported*, keyed by filing date | Kills look-ahead/restatement; the quality gate must see only what was public at each month-end |
| R2 | **Survivorship-free price history** incl. delisted names (total-return adjusted) | A name that craters and delists must show the loss, not vanish |
| R3 | **Point-in-time universe membership** (historical large-cap / Russell-1000-top-half constituents per date) | The funnel must screen the universe *as it was*, including names later removed |
| R4 | **Reporting-lag discipline** — use a record only once its filing date ≤ as_of | No "earnings we hadn't seen yet" |

## Data sources (the actual decision)

| Source | Covers | Notes / rough cost (retail) |
|---|---|---|
| **Sharadar** (Nasdaq Data Link) | PIT fundamentals (SF1, `dimension=ARQ` as-reported, `datekey` = filing date), prices (SEP), delistings/tickers, some index membership | Best PIT-fundamentals fit for a retail budget; ~$ tens/mo. Strong R1+R2+R4 |
| **Norgate Data** | Survivorship-free US prices + historical index constituents (incl. delisted) | Best R2+R3; no deep fundamentals. ~$ tens/mo (Windows-oriented) |
| **Compustat Point-in-Time** | Gold-standard PIT fundamentals + CRSP prices | Institutional pricing; overkill unless you have access |
| **FMP / Tiingo** | Historical fundamentals + prices | Mostly *restated*, partial PIT — does **not** satisfy R1 cleanly |

**Recommended:** Sharadar alone satisfies R1/R2/R4 and partial R3; pair with **Norgate** if you
want rigorous R3 index membership. Phase it (below) so you get the biggest bias fix first.

## Architecture — reuse the existing `DataProvider` protocol

The engine already talks only to `DataProvider` (`src/momentum/providers/base.py`), and the
protocol signature is *already point-in-time-shaped*: `price_history(ticker, as_of)` and
`info(ticker, as_of)`. So most of the work is a new provider, not engine surgery.

1. **New provider** `providers/sharadar_provider.py` implementing the protocol:
   - `price_history(t, as_of)` → SEP total-return prices ≤ as_of, **including delisted tickers**.
   - `info(t, as_of)` → the latest SF1 `ARQ` record with `datekey ≤ as_of` (as-first-reported),
     mapped into the same `info`-dict keys `extract_fundamentals` expects (FCF, netIncome→
     `netIncomeToCommon`, OCF, ROA, margins, revenue, etc.). **This is the whole PIT trick** —
     same interface, as-of-correct values. Snapshot-cache it exactly like the yfinance provider.
2. **Point-in-time universe.** Add a `universe_asof(as_of) -> list[str]` source (Sharadar index
   tables or Norgate constituents) and have the backtester call it per month instead of the fixed
   `load_tickers(path)` list. New small module `universe_history.py`; `universe.py` stays for live.
3. **Backtester changes** (`backtest.py`):
   - Per rebalance month: `tickers = universe_asof(m)` (incl. names later delisted).
   - Drop the `--fundamentals skip/approx` fork — with a PIT provider the **full funnel runs
     faithfully**, fundamentals included. Keep `skip` only as a fast price-only diagnostic.
   - Preload histories for the *union* of all months' constituents (so delisted names are present
     for the months they existed).
   - Everything else (accordion, sell-discipline reconciliation, metrics vs benchmark) is unchanged.

## PIT-integrity safeguards (build these as asserts/tests)

- **No look-ahead:** assert every fundamental record used has `datekey ≤ as_of` (R1/R4).
- **As-reported, not restated:** use Sharadar `dimension=ARQ` (or first vintage), never `MRQ`.
- **Membership as-of:** assert the universe for month *m* is built from `universe_asof(m)`, never
  today's list.
- **Delisting realized:** a name that delists mid-hold takes its final return then exits to cash
  next rebalance (don't forward-fill a dead price).
- **Sanity spot-checks (tests):** a known delisted name (e.g. a 2008 financial) appears in the
  pre-delisting universe and is gone after; a fundamental value as-of a historical date matches
  the actual filing.

## Phasing & effort

- **Phase 1 — survivorship fix (biggest bang):** wire survivorship-free prices + PIT universe
  (Norgate or Sharadar SEP/tickers). Run the **price-based** funnel faithfully. Removes the worst
  bias for modest effort. ~2–3 days once data access exists.
- **Phase 2 — PIT fundamentals:** add the Sharadar `info(t, as_of)` path; full funnel incl.
  quality gate. ~2–3 days.
- **Phase 3 — validation:** the integrity asserts/tests above; reconcile a short window against a
  known reference. ~1 day.

## Interim stance (until Phase 1 ships)

- Treat the yfinance backtest as a **directional** logic check only.
- **Paper-trade now** (`RUNBOOK.md`): every live month-end banks a clean point-in-time snapshot in
  `data/cache/<as_of>/`. In a year, that forward record is the most trustworthy validation set you
  have — zero survivorship, zero look-ahead — and it costs nothing but running the monthly ritual.
