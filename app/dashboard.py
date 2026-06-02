"""Momentum Sleeve — local Streamlit dashboard.

Run with:  streamlit run app/dashboard.py

Four views over the same deterministic engine the CLI uses: Screen, Holdings/Sell,
Rebalance, and Backtest. All runs go through the dated snapshot cache, so repeated
interactions are fast and reproducible.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# Make src/ importable when run via `streamlit run app/dashboard.py`.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from momentum.backtest import run_backtest  # noqa: E402
from momentum.config import load_config  # noqa: E402
from momentum.holdings import load_holdings  # noqa: E402
from momentum.portfolio import build_target_book  # noqa: E402
from momentum.providers import YFinanceProvider  # noqa: E402
from momentum.reconstitution import build_plan  # noqa: E402
from momentum.report import drop_breakdown, target_weight_table  # noqa: E402
from momentum.screener import run_screen  # noqa: E402
from momentum.universe import load_tickers  # noqa: E402

st.set_page_config(page_title="Momentum Sleeve", layout="wide")


@st.cache_resource
def get_config(path: str):
    return load_config(path)


def get_provider(cfg):
    return YFinanceProvider(
        cache_dir=cfg.data.cache_dir, history_years=cfg.data.price_history_years
    )


@st.cache_data(show_spinner="Running screen…")
def cached_screen(config_path: str, universe_path: str, as_of: str):
    cfg = load_config(config_path)
    provider = YFinanceProvider(cfg.data.cache_dir, cfg.data.price_history_years)
    tickers = load_tickers(universe_path)
    result = run_screen(provider, tickers, date.fromisoformat(as_of), cfg)
    book = build_target_book(result.selected["ticker"].tolist(), cfg.portfolio)
    return result, book


# ----------------------------------------------------------------- sidebar
st.sidebar.title("⚙️ Momentum Sleeve")
config_path = st.sidebar.text_input("Config", "config/strategy.yaml")
cfg = get_config(config_path)

universe_files = sorted(str(p) for p in Path("data/universe").glob("*"))
universe_path = st.sidebar.selectbox(
    "Universe file", universe_files or ["data/universe/example_universe.txt"]
)
as_of = st.sidebar.date_input("As of (month-end)", date(2025, 5, 30))
st.sidebar.caption(
    f"N_max {cfg.portfolio.n_max} · {cfg.portfolio.weight_per_name:.1%}/name · "
    f"cash {cfg.portfolio.cash_ticker} · HALO {cfg.halo.mode}"
)

tab_screen, tab_holdings, tab_rebal, tab_bt = st.tabs(
    ["🔎 Screen", "📉 Holdings / Sell", "🔁 Rebalance", "📊 Backtest"]
)


def _fmt(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col, f in {
        "momentum": "{:.1%}", "pct_off_high": "{:.1%}", "rsi": "{:.0f}",
        "pcf": "{:.1f}", "quality_score": "{:.2f}",
    }.items():
        if col in out:
            out[col] = out[col].map(lambda v: f.format(v) if pd.notna(v) else "—")
    if "market_cap" in out:
        out["market_cap"] = out["market_cap"].map(
            lambda v: f"${v/1e9:.0f}B" if pd.notna(v) else "—"
        )
    return out


# =============================================================== Screen tab
with tab_screen:
    st.header("Monthly screen")
    if st.button("Run screen", type="primary", key="run_screen"):
        st.session_state["screen"] = cached_screen(
            config_path, universe_path, as_of.isoformat()
        )

    if "screen" in st.session_state:
        result, book = st.session_state["screen"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Scanned", len(result.audit))
        c2.metric("Qualified", len(result.survivors))
        c3.metric("Selected", book.n_equity)
        c4.metric(f"Cash ({book.cash_ticker})", f"{book.cash_weight:.1%}")
        if book.below_floor:
            st.warning(
                f"Only {book.n_equity} names qualified — below the "
                f"{cfg.portfolio.min_names_floor}-name floor. Cash grows; "
                "exposure is not forced."
            )

        left, right = st.columns([3, 2])
        with left:
            st.subheader("Selected book (ranked by composite momentum)")
            cols = [c for c in ["rank", "ticker", "sector", "halo", "momentum",
                                "pct_off_high", "rsi", "pcf", "quality_score",
                                "quality_unverified", "skipped_checks",
                                "market_cap"] if c in result.selected.columns]
            st.dataframe(_fmt(result.selected[cols]), hide_index=True,
                         use_container_width=True)
            st.caption("HALO is observational only (not gating). `quality_unverified` = cleared "
                       "a quality check only because a field was missing (skip policy).")
        with right:
            st.subheader("Drops by funnel stage")
            db = drop_breakdown(result)
            fig = go.Figure(go.Bar(x=db.values, y=db.index, orientation="h"))
            fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Target weights")
            st.markdown(target_weight_table(book, result.selected))

        with st.expander("Full audit trail (every ticker, stage, reason)"):
            audit_cols = [c for c in ["ticker", "stage", "status", "reason", "sector",
                                      "halo", "momentum", "pct_off_high", "pcf",
                                      "quality_score", "market_cap"]
                          if c in result.audit.columns]
            st.dataframe(_fmt(result.audit[audit_cols]), hide_index=True,
                         use_container_width=True)
    else:
        st.info("Pick a universe + date in the sidebar, then **Run screen**.")


# ====================================================== Holdings / Sell tab
with tab_holdings:
    st.header("Sell-discipline review (§7)")
    uploaded = st.file_uploader("Upload current holdings CSV", type=["csv"])
    default_holdings = "data/holdings/example_holdings.csv"
    use_example = st.checkbox(
        "Use example holdings", value=not uploaded and Path(default_holdings).exists()
    )
    contribution = st.number_input("New contribution ($) for Smart-Buy", 0.0,
                                   step=1000.0, value=0.0)

    if st.button("Evaluate holdings", type="primary", key="run_recon"):
        if uploaded is not None:
            tmp = Path("data/holdings/_uploaded.csv")
            tmp.write_bytes(uploaded.getvalue())
            holdings_path = str(tmp)
        elif use_example:
            holdings_path = default_holdings
        else:
            st.error("Provide a holdings CSV or tick 'Use example holdings'.")
            st.stop()

        provider = get_provider(cfg)
        tickers = load_tickers(universe_path)
        holdings = load_holdings(holdings_path)
        with st.spinner("Screening + evaluating holdings…"):
            result, plan = build_plan(
                provider, cfg, as_of, tickers, holdings, contribution
            )
        st.session_state["recon"] = (result, plan)

    if "recon" in st.session_state:
        result, plan = st.session_state["recon"]
        ev = plan.holdings_eval
        sells = int((ev["action"] == "SELL").sum()) if not ev.empty else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("SELL", sells)
        c2.metric("HOLD", len(ev) - sells)
        c3.metric("New book size", plan.book.n_equity)

        def _hl(row):
            color = "#5b1a1a" if row["action"] == "SELL" else "#14361f"
            return [f"background-color: {color}"] * len(row)

        if not ev.empty:
            st.dataframe(ev.style.apply(_hl, axis=1), hide_index=True,
                         use_container_width=True)
        st.session_state["plan"] = plan
    else:
        st.info("Upload holdings (or use the example), then **Evaluate holdings**.")


# ============================================================= Rebalance tab
with tab_rebal:
    st.header("Reconstitution plan")
    if "plan" in st.session_state:
        plan = st.session_state["plan"]
        result, _ = st.session_state["recon"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Add", len(plan.adds))
        c2.metric("Delete", len(plan.deletes))
        c3.metric("Retain", len(plan.retained))
        st.write(f"**Add:** {', '.join(plan.adds) or '—'}")
        st.write(f"**Delete:** {', '.join(plan.deletes) or '—'}")
        st.write(f"**Retain:** {', '.join(plan.retained) or '—'}")

        st.subheader("Target weights")
        st.markdown(target_weight_table(plan.book, result.selected))

        if plan.smart_buy:
            st.subheader(f"Smart-Buy allocation of ${plan.contribution:,.0f}")
            sb = pd.DataFrame(
                [{"ticker": t, "buy_$": v} for t, v in plan.smart_buy.items()]
            )
            st.dataframe(sb, hide_index=True, use_container_width=True)
            st.caption("Routes new cash to underweights only — no forced taxable sells.")
    else:
        st.info("Run **Evaluate holdings** first to generate a reconstitution plan.")


# ============================================================== Backtest tab
with tab_bt:
    st.header("Walk-forward backtest")
    c1, c2, c3 = st.columns(3)
    bt_start = c1.date_input("Start", date.fromisoformat(cfg.backtest.start))
    bt_end = c2.date_input("End", date.fromisoformat(cfg.backtest.end))
    fmode = c3.selectbox("Fundamentals", ["skip", "approx"], index=0,
                         help="skip = faithful price-based gates; approx = look-ahead biased")
    st.caption(
        "⚠️ skip mode runs technical+momentum only (yfinance has no point-in-time "
        "fundamentals). Fixed universe = survivorship bias."
    )

    if st.button("Run backtest", type="primary", key="run_bt"):
        provider = get_provider(cfg)
        with st.spinner("Backtesting…"):
            run_backtest(provider, cfg, universe_path,
                         bt_start.isoformat(), bt_end.isoformat(), fundamentals=fmode)
        st.session_state["bt"] = True

    curve_path = Path(cfg.data.out_dir) / "backtest" / "equity_curve.csv"
    metrics_path = Path(cfg.data.out_dir) / "backtest" / "metrics.json"
    if st.session_state.get("bt") and curve_path.exists():
        import json
        hist = pd.read_csv(curve_path, parse_dates=["date"]).set_index("date")
        metrics = json.loads(metrics_path.read_text())

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist["equity"], name="Strategy"))
        fig.add_trace(go.Scatter(x=hist.index, y=hist["bench_equity"],
                                 name=cfg.backtest.benchmark))
        fig.update_layout(height=380, title="Equity curve",
                          margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

        dd = hist["equity"] / hist["equity"].cummax() - 1
        ddfig = go.Figure(go.Scatter(x=hist.index, y=dd, fill="tozeroy",
                                     name="Drawdown"))
        ddfig.update_layout(height=240, title="Strategy drawdown",
                            margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(ddfig, use_container_width=True)

        s, b, e = metrics["strategy"], metrics["benchmark"], metrics["extra"]
        mt = pd.DataFrame({
            "Metric": ["Total return", "CAGR", "Ann vol", "Max drawdown",
                       "Sharpe", "Hit rate"],
            "Strategy": [s["total_return"], s["cagr"], s["ann_vol"],
                         s["max_drawdown"], s["sharpe"], s["hit_rate"]],
            cfg.backtest.benchmark: [b["total_return"], b["cagr"], b["ann_vol"],
                                     b["max_drawdown"], b["sharpe"], b["hit_rate"]],
        })
        st.dataframe(mt, hide_index=True, use_container_width=True)
        st.caption(
            f"Avg names {e['avg_n_equity']:.1f} · avg cash {e['avg_cash_weight']:.1%} · "
            f"turnover {e['avg_turnover']:.1%} · win-vs-bench {e['win_vs_bench']:.1%} · "
            f"fundamentals={e['fundamentals_mode']}"
        )
    else:
        st.info("Set a window and **Run backtest**.")
