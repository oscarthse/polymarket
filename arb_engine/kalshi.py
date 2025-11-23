import os
from typing import Any, Dict, List, Optional

from kalshi_client import KalshiClient

from .models import MarketQuote

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"

KALSHI_API_KEY = os.getenv("KALSHI_API_KEY")
KALSHI_KEY_PATH = os.getenv("KALSHI_API_SECRET_PATH")


async def load_kalshi_quotes() -> List[MarketQuote]:
    """Fetch open markets from Kalshi and convert to MarketQuote objects.

    Uses:
      - kalshi_client.KalshiClient (synchronous under the hood)
      - Prices in cents (0–100), converted to decimal (0–1)
    """
    if not KALSHI_API_KEY or not KALSHI_KEY_PATH:
        raise ValueError(
            "Kalshi API key or secret path missing. Set KALSHI_API_KEY and "
            "KALSHI_API_SECRET_PATH environment variables."
        )

    client = KalshiClient(
        api_key_id=KALSHI_API_KEY,
        private_key_path=KALSHI_KEY_PATH,
        base_url=KALSHI_BASE,
    )

    all_markets: List[Dict[str, Any]] = []
    page = 1
    max_pages = 3  # 3 * 100 = 300 markets

    while page <= max_pages:
        try:
            response = await client.get(
                "/markets",
                params={
                    "limit": 100,
                    "offset": (page - 1) * 100,
                    "status": "open",
                },
            )
            response.raise_for_status()
            data = response.json()
            markets = data.get("markets", [])
            if not markets:
                break

            all_markets.extend(markets)
            print(
                f"  Debug: Kalshi page {page}: got {len(markets)} markets, "
                f"total so far: {len(all_markets)}"
            )

            if len(markets) < 100:
                break  # last page
            page += 1
        except Exception as e:  # noqa: BLE001
            print(f"  Error fetching Kalshi markets (page {page}): {e}")
            break

    print(f"  Debug: Kalshi API returned {len(all_markets)} raw markets")

    quotes: List[MarketQuote] = []
    skipped_status = 0
    skipped_missing_prices = 0

    if all_markets:
        first = all_markets[0]
        print(f"  Debug: First Kalshi market keys: {list(first.keys())}")
        print(
            f"  Debug: First market - title: '{first.get('title')}', "
            f"status: {first.get('status')}"
        )
        print("  Debug: First market price fields:")
        for field in [
            "yes_ask",
            "yes_bid",
            "no_ask",
            "no_bid",
            "last_price",
            "yes_ask_dollars",
            "yes_bid_dollars",
            "no_ask_dollars",
            "no_bid_dollars",
        ]:
            if field in first:
                print(f"    {field}: {first.get(field)}")

    for m in all_markets:
        status = str(m.get("status", "")).lower()
        if status in {"closed", "settled", "cancelled"}:
            skipped_status += 1
            continue

        # Raw prices in cents
        yes_ask_raw = m.get("yes_ask")
        yes_bid_raw = m.get("yes_bid")
        no_ask_raw = m.get("no_ask")
        no_bid_raw = m.get("no_bid")
        last_price_raw = m.get("last_price")

        # BUY prices (asks) in decimal 0–1
        yes_buy: Optional[float] = None
        no_buy: Optional[float] = None

        if isinstance(yes_ask_raw, (int, float)) and yes_ask_raw > 0:
            yes_buy = yes_ask_raw / 100.0
        elif isinstance(last_price_raw, (int, float)) and last_price_raw > 0:
            yes_buy = last_price_raw / 100.0

        if isinstance(no_ask_raw, (int, float)) and no_ask_raw > 0:
            no_buy = no_ask_raw / 100.0
        elif isinstance(last_price_raw, (int, float)) and last_price_raw > 0:
            no_buy = (100.0 - last_price_raw) / 100.0

        # SELL prices (bids) in decimal 0–1
        yes_sell: Optional[float] = None
        no_sell: Optional[float] = None

        if isinstance(yes_bid_raw, (int, float)) and yes_bid_raw > 0:
            yes_sell = yes_bid_raw / 100.0
        if isinstance(no_bid_raw, (int, float)) and no_bid_raw > 0:
            no_sell = no_bid_raw / 100.0

        # We require both YES and NO buy prices for our arbitrage logic
        if yes_buy is None or not (0 < yes_buy < 1):
            skipped_missing_prices += 1
            continue
        if no_buy is None or not (0 < no_buy < 1):
            skipped_missing_prices += 1
            continue

        quotes.append(
            MarketQuote(
                platform="kalshi",
                market_id=str(m.get("ticker") or m.get("market_id") or ""),
                question=(
                    m.get("title")
                    or m.get("question")
                    or m.get("subtitle")
                    or ""
                ),
                yes_buy=yes_buy,
                no_buy=no_buy,
                yes_sell=yes_sell,
                no_sell=no_sell,
                extra={"raw": m},
            )
        )

    print(f"  → Loaded {len(quotes)} Kalshi quotes")
    if skipped_status or skipped_missing_prices:
        print(
            f"    Skipped: {skipped_status} closed/settled/cancelled, "
            f"{skipped_missing_prices} missing/invalid prices"
        )
    if quotes:
        print("    Sample markets:")
        for i, q in enumerate(quotes[:5], 1):
            print(
                f"      {i}. {q.question[:70]}... "
                f"(YES: {q.yes_buy:.3f}, NO: {q.no_buy:.3f})"
            )

    return quotes
