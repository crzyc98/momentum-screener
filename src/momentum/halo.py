"""HALO tagging — Heavy Assets, Low Obsolescence.

v1 policy (deliberate): a *deterministic* sector lookup, never an LLM call. The
tag is OBSERVATIONAL — it rides along as a column and is logged, but it does NOT
gate selection or change weights. This preserves a clean pure-momentum+quality
baseline so HALO's contribution can be measured before it's ever promoted to a
tie-breaker (v2). A stochastic semantic gate would make the strategy
non-reproducible, which is the whole thing we're avoiding.
"""

from __future__ import annotations

from momentum.config import HaloConfig


def is_halo(sector: str | None, cfg: HaloConfig) -> bool:
    """True if the name's GICS sector is in the configured heavy-asset set."""
    if sector is None:
        return False
    return sector.strip() in set(cfg.heavy_asset_sectors)
