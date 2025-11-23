"""Core data models for the arbitrage engine."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class MarketQuote:
    """Normalized market data from an exchange.

    Attributes:
        platform: Source exchange name (e.g., "kalshi", "polymarket").
        market_id: Exchange-specific identifier for the market.
        question: Human-readable market title/question.
        yes_buy: Best available buy price for "YES" as a decimal between 0 and 1.
        no_buy: Best available buy price for "NO" as a decimal between 0 and 1.
        yes_sell: Best available sell price for "YES" (optional).
        no_sell: Best available sell price for "NO" (optional).
        extra: Raw exchange payload for debugging/inspection.
    """

    platform: str
    market_id: str
    question: str
    yes_buy: float
    no_buy: float
    yes_sell: Optional[float] = None
    no_sell: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)
