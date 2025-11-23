# Polymarket-Kalshi Arbitrage Scanner

Cross-platform arbitrage detection engine that scans for price discrepancies between Polymarket and Kalshi.

## Quick Start

### 1. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -e .
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Kalshi API Credentials
KALSHI_API_KEY=your-api-key-id-here
KALSHI_API_SECRET_PATH=/path/to/your/kalshi_private_key.pem
```

**Where to get these:**
- **KALSHI_API_KEY**: Your API key ID from [Kalshi Account Settings](https://kalshi.com/account/profile) → API Keys
- **KALSHI_API_SECRET_PATH**: Path to your RSA private key PEM file (the one you generated and uploaded the public key for)

### 3. Run the Scanner

```bash
python polymarket_arb_scanner.py
```

Or using `uv`:
```bash
uv run polymarket_arb_scanner.py
```

## What It Does

1. **Fetches Polymarket data** from Gamma API (events) and CLOB API (orderbooks)
2. **Fetches Kalshi data** using authenticated RSA-signed requests
3. **Matches markets** across platforms using fuzzy string matching
4. **Detects arbitrage opportunities** where prices differ by at least 2%

## Output

The scanner prints JSON-formatted arbitrage opportunities:

```json
[
  {
    "type": "cross_yes",
    "poly_yes": 0.45,
    "kalshi_yes": 0.50,
    "spread": 0.05,
    "poly_market": "Will X happen?",
    "kalshi_market": "Will X happen?"
  }
]
```

## Requirements

- Python 3.13+
- Kalshi API credentials (API key ID + RSA private key)
- Internet connection

## Troubleshooting

**"Kalshi API key or secret path missing"**
- Make sure your `.env` file exists and has both variables set
- Check that the private key file path is correct and the file exists

**"Private key file not found"**
- Verify the path in `KALSHI_API_SECRET_PATH` is correct
- Use absolute path if relative path doesn't work

**"Failed to load private key"**
- Ensure your private key is in PEM format
- Check that the file is readable

**Authentication errors from Kalshi**
- Verify your API key ID is correct
- Ensure the public key associated with your private key is registered in Kalshi
- Check that your API key is active in Kalshi account settings

## Project Structure

```
polymarket/
├── polymarket_arb_scanner.py  # Main scanner
├── kalshi_auth.py             # RSA-PSS signing
├── kalshi_client.py           # Authenticated HTTP client
├── pyproject.toml             # Dependencies
└── .env                       # Your credentials (not in git)
```

## Notes

- The scanner uses a 0.55 similarity threshold for market matching (adjustable in code)
- Minimum arbitrage edge is set to 2% (0.02) - also adjustable
- Polymarket data is fetched from public APIs (no auth required)
- Kalshi requires RSA-PSS authentication (handled automatically)

