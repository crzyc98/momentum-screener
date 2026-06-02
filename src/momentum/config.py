"""Typed, validated strategy configuration.

All dials live in ``config/strategy.yaml``; this module loads and validates them
into immutable dataclasses so the rest of the engine never touches raw YAML or
magic numbers.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path("config/strategy.yaml")


class UniverseConfig(BaseModel):
    market_cap_floor: float
    min_price: float
    min_avg_dollar_volume: float
    adv_lookback_days: int = 20


class FundamentalConfig(BaseModel):
    require_positive_trailing_eps_growth: bool = True
    require_positive_forward_eps_growth: bool = True
    pcf_top_quartile: bool = True
    pcf_quantile: float = 0.25
    quality_top_tier: bool = True
    quality_quantile: float = 0.50


class TechnicalConfig(BaseModel):
    price_above_50sma: bool = True
    golden_cross_50_over_200: bool = True
    within_pct_of_52w_high: float = 0.05


class MomentumConfig(BaseModel):
    lookbacks_months: list[int] = Field(default_factory=lambda: [3, 6, 9])
    skip_recent_days: int = 5


class PortfolioConfig(BaseModel):
    n_max: int = 40
    weight_per_name: float = 0.025
    min_names_floor: int = 25
    cash_ticker: str = "BIL"


class SellConfig(BaseModel):
    sma50_buffer_pct: float = 0.02
    drop_if_out_of_top_n: bool = True
    drop_if_off_screener: bool = True
    rs_breakdown_lookback_days: int = 63
    rs_breakdown_threshold: float = 0.0


class HaloConfig(BaseModel):
    mode: str = "observational"
    heavy_asset_sectors: list[str] = Field(default_factory=list)


class BacktestConfig(BaseModel):
    benchmark: str = "SPY"
    start: str = "2018-01-01"
    end: str = "2024-12-31"
    initial_capital: float = 100_000
    rebalance: str = "month_end"


class DataConfig(BaseModel):
    cache_dir: str = "data/cache"
    out_dir: str = "data/out"
    price_history_years: int = 3


class Config(BaseModel):
    universe: UniverseConfig
    fundamental: FundamentalConfig
    technical: TechnicalConfig
    momentum: MomentumConfig
    portfolio: PortfolioConfig
    sell: SellConfig
    halo: HaloConfig
    backtest: BacktestConfig
    data: DataConfig


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    """Load and validate the strategy config from YAML."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Strategy config not found: {path}")
    raw = yaml.safe_load(path.read_text())
    return Config.model_validate(raw)
