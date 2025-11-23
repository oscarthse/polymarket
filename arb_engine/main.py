"""Entry point for quick manual checks.

This script currently focuses on verifying connectivity to Kalshi by loading
market quotes with authentication. It prints a small sample so users can see
output when running `uv run -m arb_engine.main`.
"""

import asyncio

from .kalshi import load_kalshi_quotes


async def main() -> None:
    """Fetch Kalshi markets and print a short summary."""

    print("[arb_engine] Loading Kalshi markets...")
    quotes = await load_kalshi_quotes()

    print(f"[arb_engine] Loaded {len(quotes)} markets")
    if not quotes:
        print("[arb_engine] No markets returned. Check credentials or API availability.")
        return

    print("[arb_engine] Sample:")
    for quote in quotes[:5]:
        print(
            f"  - {quote.question[:80]}... "
            f"(YES buy {quote.yes_buy:.3f}, NO buy {quote.no_buy:.3f})"
        )


if __name__ == "__main__":
    asyncio.run(main())
