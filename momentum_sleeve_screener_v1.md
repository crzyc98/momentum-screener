# Momentum Sleeve — Screener & Rulebook **v1**
*Porterhouse-style, built for execution inside a single Fidelity Basket Portfolio*

> **What this is:** a transparent, rules-based monthly screen + reconstitution process. The rules pick the names; you place the order. Not investment advice. Absolute-momentum strategies trade whipsaw risk for crash protection — expect to be occasionally sold out of a name that recovers, and occasionally sitting in T-bills during a violent bottom. That's the deal.

> **Provenance key:** `[P]` = confirmed Porterhouse-documented · `[D]` = our design dial (reasonable reconstruction, tune freely) · `[F]` = Fidelity-mechanics constraint we're designing around.

---

## 1. The funnel (run on the last trading day of each month)

```
Russell 1000 top half          [P]
        │  liquidity / size floor
        ▼
FUNDAMENTAL QUALITY GATE        [P] earnings + cash-flow strength
        │
        ▼
(optional) HALO TILT            [P concept / D as hard gate]
        │
        ▼
TECHNICAL / MOMENTUM GATE       [D] trend structure + near highs
        │  rank survivors by composite momentum
        ▼
TOP N → basket   |   shortfall → T-bill sleeve (the "accordion")
```

---

## 2. Universe & liquidity `[P]`

| Setting | Value | Note |
|---|---|---|
| Index proxy | Russell 1000, top ~50% by market cap | ≈ the 500 largest US names |
| Market-cap floor | **≥ $20B** `[D]` | Calibrate toward the ~500-largest cutoff; raise if you want it tighter |
| Price | ≥ $5; avg daily $ volume healthy | market-orders-only basket → stay liquid `[F]` |
| Exclude | OTC, ADRs if you prefer domestic, anything illiquid | |

## 3. Fundamental quality gate `[P]`

Porterhouse screens for "strong earnings and cash flows." Concrete proxies in Fidelity's screener:

- **Earnings:** positive trailing **and** forward EPS growth (avoid negative-earnings momentum traps)
- **Cash flow:** **Price-to-Cash-Flow** in the top quartile of the universe (cash flow is harder to manipulate than GAAP EPS — this is the real quality signal)
- **Quality score:** S&P Global / Fidelity quantitative quality rating in the top tier
- A name must clear **all three** to advance.

## 4. HALO tilt — *optional overlay* `[P concept]` / `[D as a hard gate]`

Brown's "heavy assets, low obsolescence" idea: favor businesses AI can't replace (energy, materials, food/drink, logistics, hospitality, aerospace, building materials), where automation *expands* margins rather than threatens the core product.

- **As a soft tilt (recommended for v1):** if two names rank similarly on momentum, prefer the HALO one. Keep it a tie-breaker, not a wall.
- **As a hard gate (what the doc implies):** discard any name whose core product an LLM could plausibly obsolete. *Caution:* the real Porterhouse already excludes the Mag 7, so a hard HALO gate is directionally consistent — but it will also bench a lot of strong tech momentum. Decide deliberately; don't let it run silently.

## 5. Technical / momentum gate `[D]`

These thresholds are our calibration, not disclosed Porterhouse rules.

**Trend structure (must pass all):**
- Price > 50-day SMA
- 50-day SMA > 200-day SMA (confirmed uptrend / "golden cross" regime)
- Within **5%** of 52-week high (currently leading, not recovering)

**Then rank the survivors** by a **composite momentum score** — average of total return over **3, 6, and 9-month** lookbacks (skip the most recent ~1 week to dodge short-term reversal noise). 6–12 month windows are the academic sweet spot; the blend smooths regime sensitivity.

## 6. Portfolio construction & the cash accordion

| Parameter | v1 setting | Provenance |
|---|---|---|
| Max equity names (N_max) | **40** | `[D]` — your 25–45 range; real Porterhouse ~58 and flexible |
| Weighting | **Equal, 2.5% each** | `[D]` |
| Cash vehicle | **BIL or SHV** as a permanent basket member | `[D]` implements `[P]` accordion |
| Accordion rule | If only N qualify (N < 40): equity = N × 2.5%, **remainder → T-bill sleeve** | `[P]` |
| Floor | If a brutal tape leaves < ~25 names, let cash grow — don't force exposure | `[P]` |

This is the mechanism: you never pad the book with marginal names to stay fully invested. Fewer qualifiers = more T-bills, automatically.

## 7. Sell discipline `[D]` — exit ≠ inverse of entry

A held name is **excised** at month-end if **any** trigger fires:
- Price closes below 50-day SMA (meaningfully, e.g. > ~2%), **or**
- Falls out of the top-N composite-momentum rank, **or**
- Drops off the screener entirely (failed a fundamental/technical gate), **or**
- Sustained relative-strength breakdown vs. the index.

Letting winners run is both the tax-smart move (FIFO sells low-basis lots first — so *don't* trim, only exit) and the momentum-correct move. Same action, two reasons.

## 8. The monthly operating ritual (ties to basket mechanics)

1. **Re-rank** the universe via the Fidelity screener → new buy list.
2. **Sell screen:** evaluate current holdings against §7. Tag exits.
3. **Edit the basket:** delete exits, add new entrants at target weight, reset weights. (Constituent rotation inside the basket = still one block trade per your policy.) `[F]`
4. **Deploy the contribution:** add new cash via **Smart Buy → "use target weights"** so it flows to the freshly-added entrants (now the underweights) — momentum-in without selling. `[F]`
5. **Rebalance/Place order** — one click, one block trade, ~3 blocks/quarter.
6. **Never** use the sell-outside-and-move-back-in trick for routine FIFO dodging — that re-incurs an individual block trade. Reserve it only for a deliberate year-end loss harvest. `[F]`

## 9. Fidelity Stock Screener — field map (starting point)

| Screener dimension | Setting | Emulates |
|---|---|---|
| Market cap | > $20B | top-half R1000 |
| EPS growth | positive trailing + forward | earnings strength |
| Price / Cash Flow | top quartile | cash-flow quality |
| Quality rating | top tier (S&P Global) | quality overlay |
| Price vs SMA | Price > 50-SMA > 200-SMA | structural uptrend |
| 52-wk high | within 5% | current leadership |
| Sort | by 6-mo (and 3/9-mo) price performance | momentum rank |

*Field names drift as Fidelity updates the screener and its Recognia/S&P data — map to intent, not exact labels. The "RSI Turnover" filter in your source is over-specific; reproduce the* intent *(recently strong, mild healthy consolidation, trend intact) with the price-vs-SMA + %-off-high filters above plus an RSI band if exposed.*

## 10. Open dials for you to set

1. **HALO:** soft tie-breaker (my v1 default) or hard gate?
2. **N_max:** hold at 40, or push toward the real ~58?
3. **Weighting:** fixed 2.5% + cash plug (implements the accordion cleanly), or pure 1/N equal-weight always-fully-invested (drops the accordion)?
4. **Momentum metric:** the 3/6/9 blend, or a single 6-mo or 12-1 lookback?
5. **Cash sleeve:** BIL (1–3mo bills) vs SHV (≤1yr) — or skip it and stay fully invested?
6. **Exit strictness:** the 2% sub-50-SMA buffer — tighter (cut faster, more whipsaw) or looser (ride longer, deeper drawdowns)?
