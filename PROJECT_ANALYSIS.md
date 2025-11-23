# Polymarket-Kalshi Arbitrage Scanner - Project Analysis

## Project Overview

This is a **cross-platform arbitrage detection engine** that scans for price discrepancies between:
- **Polymarket** (using Gamma API for events and CLOB API for orderbooks)
- **Kalshi** (using REST API v1 for market data)

The goal is to identify arbitrage opportunities where the same event/question is priced differently across platforms.

---

## Architecture Analysis

### Current Implementation

#### 1. **Data Flow**
```
Polymarket (Gamma) → Events → Markets → Orderbooks (CLOB) → Quotes
Kalshi (REST API) → Markets → Quotes
↓
Market Matching (fuzzy string matching)
↓
Arbitrage Detection (price spread analysis)
```

#### 2. **Key Components**

**Data Models:**
- `MarketQuote`: Represents a single market quote with yes/no prices
- `MatchedMarket`: Pairs matching markets from both platforms with similarity score

**Polymarket Integration:**
- ✅ **Working**: Uses public APIs (no auth required)
- ✅ Fetches events from Gamma API
- ✅ Fetches orderbooks from CLOB API
- ✅ Extracts best ask prices for YES tokens

**Kalshi Integration:**
- ❌ **BROKEN**: Uses incorrect authentication method
- ❌ Attempts to use header-based auth (`kalshi-api-key`, `kalshi-api-secret`)
- ❌ Kalshi requires RSA-PSS signing, not header secrets
- ⚠️ Private key is loaded but never used

**Market Matching:**
- Uses `difflib.get_close_matches()` for fuzzy string matching
- Similarity threshold: 0.55 (configurable)
- Matches based on question/title text

**Arbitrage Detection:**
- Detects YES→YES spreads (buy Poly, sell Kalshi)
- Detects NO→NO spreads (buy Poly NO, sell Kalshi NO)
- Minimum edge threshold: 0.02 (2%)

---

## Critical Issues Identified

### 🔴 **CRITICAL: Kalshi Authentication Broken**

**Problem:**
```python
# Line 131-134: INCORRECT
headers = {
    "kalshi-api-key": KALSHI_API_KEY,
    "kalshi-api-secret": KALSHI_API_SECRET,  # ❌ Variable doesn't exist!
}
```

**Issues:**
1. `KALSHI_API_SECRET` is referenced but never defined (only `KEY_PATH` exists)
2. Kalshi API **does not accept** header-based secrets
3. Kalshi requires **RSA-PSS signature authentication**
4. Private key is loaded (line 35-36) but never used

**Required Solution:**
- Implement RSA-PSS signing with SHA256
- Use headers: `KALSHI-ACCESS-KEY`, `KALSHI-ACCESS-SIGNATURE`, `KALSHI-ACCESS-TIMESTAMP`
- Sign message format: `{timestamp}{method}{path}`

### 🟡 **Code Quality Issues**

1. **Line 231**: Typo - `m.kalshiquestion` should be `m.kalshi.question`
2. **Line 252**: Variable `arbs` is referenced but assignment might be missing (though it should be from `detect_cross_arbitrage()`)
3. **Error Handling**: Limited error handling for API failures
4. **Rate Limiting**: No rate limiting implemented for API calls
5. **Async Safety**: Private key loading happens at module level (line 35-36), which could fail if file doesn't exist

### 🟢 **Design Considerations**

1. **Market Matching**: Fuzzy matching with 0.55 threshold may produce false positives
2. **Price Extraction**: Kalshi price extraction assumes `yes_bid` exists and is in cents (divided by 100)
3. **Arbitrage Logic**: Only detects simple spreads, doesn't account for:
   - Trading fees
   - Slippage
   - Execution time
   - Market depth

---

## Dependencies Analysis

### Current Dependencies (`pyproject.toml`):
- `httpx>=0.28.1` ✅ (async HTTP client)
- `python-dotenv>=1.2.1` ✅ (env var loading)
- `requests>=2.32.5` ⚠️ (not used in main scanner, only in test.ipynb)
- `numpy>=2.3.5` ⚠️ (not used anywhere)
- `ipykernel>=7.1.0` ✅ (for Jupyter notebooks)

### Missing Dependencies:
- ❌ **`cryptography`** - Required for RSA signing

---

## Environment Variables

### Required:
- `KALSHI_API_KEY` - Kalshi API Key ID (from account settings)
- `KALSHI_API_SECRET_PATH` - Path to RSA private key PEM file

### Optional:
- None currently

---

## File Structure

```
polymarket/
├── main.py                    # Simple hello world (unused)
├── polymarket_arb_scanner.py  # Main arbitrage scanner (262 lines)
├── test.ipynb                 # Jupyter notebook with bundle arb experiments
├── pyproject.toml             # Dependencies
├── README.md                  # Empty
├── .gitignore                 # Excludes .venv, __pycache__, kalshi_private_key.pem
└── .env                       # Not tracked (should contain secrets)
```

---

## Implementation Plan

### Phase 1: Fix Kalshi Authentication ✅
1. Add `cryptography` dependency
2. Create `kalshi_auth.py` with RSA-PSS signing logic
3. Create `kalshi_client.py` with authenticated HTTP client
4. Update `polymarket_arb_scanner.py` to use new client

### Phase 2: Code Quality Fixes
1. Fix typo on line 231
2. Add proper error handling
3. Move private key loading to function (lazy loading)
4. Add validation for environment variables

### Phase 3: Enhancements (Future)
1. Add rate limiting
2. Add trading fee calculations
3. Improve market matching algorithm
4. Add execution simulation
5. Add logging/monitoring

---

## Security Considerations

1. ✅ Private key file is in `.gitignore`
2. ⚠️ Private key loaded at module level (could fail silently)
3. ⚠️ No validation of key format before use
4. ✅ Environment variables used for sensitive data

---

## Testing Status

- **Polymarket**: Appears to work (no auth required)
- **Kalshi**: **Will fail** due to incorrect authentication
- **Market Matching**: Logic appears sound
- **Arbitrage Detection**: Logic appears sound

---

## Next Steps

1. ✅ Implement RSA signing module
2. ✅ Create authenticated Kalshi client
3. ✅ Update scanner to use new client
4. ⏳ Test with real Kalshi API
5. ⏳ Add comprehensive error handling
6. ⏳ Add logging for debugging

---

*Analysis completed: 2025-01-XX*
*Last updated: After identifying RSA signing requirement*

