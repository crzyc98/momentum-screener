"""Command-line interface: ``momentum screen | reconstitute | backtest``."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from momentum.config import DEFAULT_CONFIG_PATH, load_config
from momentum.providers import YFinanceProvider


def _parse_date(s: str | None) -> date:
    if s is None:
        return date.today()
    return datetime.strptime(s, "%Y-%m-%d").date()


def _make_provider(cfg):
    return YFinanceProvider(
        cache_dir=cfg.data.cache_dir, history_years=cfg.data.price_history_years
    )


# --------------------------------------------------------------------- screen
def cmd_screen(args: argparse.Namespace) -> int:
    from momentum.portfolio import build_target_book
    from momentum.report import drop_breakdown, summary_text, write_artifacts
    from momentum.screener import run_screen
    from momentum.universe import load_tickers

    cfg = load_config(args.config)
    as_of = _parse_date(args.as_of)
    tickers = load_tickers(args.universe)
    print(f"Loaded {len(tickers)} tickers from {args.universe}")

    provider = _make_provider(cfg)
    print(f"Screening as of {as_of.isoformat()} (cache: {cfg.data.cache_dir}) ...")
    result = run_screen(provider, tickers, as_of, cfg)

    book = build_target_book(result.selected["ticker"].tolist(), cfg.portfolio)
    out = write_artifacts(result, book, cfg.data.out_dir)

    print("\n" + summary_text(result, book))
    print("\nDrops by stage:")
    for stage, count in drop_breakdown(result).items():
        print(f"  {stage:<12} {count}")
    print(f"\nArtifacts written to: {out}")
    return 0


# -------------------------------------------------------------- reconstitute
def cmd_reconstitute(args: argparse.Namespace) -> int:
    from momentum.reconstitution import run_reconstitution

    cfg = load_config(args.config)
    as_of = _parse_date(args.as_of)
    provider = _make_provider(cfg)
    run_reconstitution(
        provider=provider,
        cfg=cfg,
        as_of=as_of,
        universe_path=args.universe,
        holdings_path=args.holdings,
        contribution=args.contribution,
    )
    return 0


# ------------------------------------------------------------------ backtest
def cmd_backtest(args: argparse.Namespace) -> int:
    from momentum.backtest import run_backtest

    cfg = load_config(args.config)
    provider = _make_provider(cfg)
    run_backtest(
        provider=provider,
        cfg=cfg,
        universe_path=args.universe,
        start=args.start or cfg.backtest.start,
        end=args.end or cfg.backtest.end,
        fundamentals=args.fundamentals,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="momentum", description=__doc__)
    p.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="strategy.yaml path")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("screen", help="run the monthly funnel -> buy list + weights")
    s.add_argument("--universe", required=True, help="Fidelity CSV export or ticker list")
    s.add_argument("--as-of", help="YYYY-MM-DD (default: today)")
    s.set_defaults(func=cmd_screen)

    r = sub.add_parser("reconstitute", help="evaluate holdings + emit rebalance plan")
    r.add_argument("--universe", required=True, help="Fidelity CSV export or ticker list")
    r.add_argument("--holdings", required=True, help="current basket CSV")
    r.add_argument("--as-of", help="YYYY-MM-DD (default: today)")
    r.add_argument("--contribution", type=float, default=0.0, help="new cash to smart-buy")
    r.set_defaults(func=cmd_reconstitute)

    b = sub.add_parser("backtest", help="monthly walk-forward vs benchmark")
    b.add_argument("--universe", required=True, help="Fidelity CSV export or ticker list")
    b.add_argument("--start", help="YYYY-MM-DD (default: config)")
    b.add_argument("--end", help="YYYY-MM-DD (default: config)")
    b.add_argument(
        "--fundamentals", choices=["skip", "approx"], default="skip",
        help="skip = price-based gates only (faithful default); "
             "approx = today's fundamentals at past dates (look-ahead biased)",
    )
    b.set_defaults(func=cmd_backtest)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
