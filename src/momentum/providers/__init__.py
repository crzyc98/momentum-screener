"""Data providers. yfinance is the only v1 implementation, behind a thin protocol."""

from momentum.providers.base import DataProvider, Fundamentals, extract_fundamentals
from momentum.providers.yfinance_provider import YFinanceProvider

__all__ = ["DataProvider", "Fundamentals", "extract_fundamentals", "YFinanceProvider"]
