"""Market data: CoinMarketCap primary, CoinGecko fallback, manual override.

Network calls are best-effort; without API keys the service falls back to the
latest stored price (manual input via API/Telegram still works offline).
"""

from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import CryptoHolding, MarketPrice

CMC_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

# Minimal symbol -> CoinGecko id map for the default watchlist.
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "AVAX": "avalanche-2",
    "NEAR": "near",
    "XRP": "ripple",
    "LINK": "chainlink",
    "BNB": "binancecoin",
    "MATIC": "matic-network",
}


def fetch_price_cmc(symbol: str) -> dict | None:
    settings = get_settings()
    if not settings.coinmarketcap_api_key:
        return None
    try:
        resp = httpx.get(
            CMC_URL,
            params={"symbol": symbol.upper(), "convert": "USD"},
            headers={"X-CMC_PRO_API_KEY": settings.coinmarketcap_api_key},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()["data"][symbol.upper()]
        quote = data["quote"]["USD"]
        return {
            "symbol": symbol.upper(),
            "provider": "coinmarketcap",
            "price": quote["price"],
            "change_24h": quote.get("percent_change_24h"),
            "change_7d": quote.get("percent_change_7d"),
            "change_30d": quote.get("percent_change_30d"),
            "market_cap": quote.get("market_cap"),
            "volume_24h": quote.get("volume_24h"),
            "rank": data.get("cmc_rank"),
        }
    except Exception:
        return None


def fetch_price_coingecko(symbol: str) -> dict | None:
    coin_id = COINGECKO_IDS.get(symbol.upper())
    if not coin_id:
        return None
    try:
        resp = httpx.get(
            COINGECKO_URL,
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
            },
            timeout=10,
        )
        resp.raise_for_status()
        quote = resp.json()[coin_id]
        return {
            "symbol": symbol.upper(),
            "provider": "coingecko",
            "price": quote["usd"],
            "change_24h": quote.get("usd_24h_change"),
            "market_cap": quote.get("usd_market_cap"),
            "volume_24h": quote.get("usd_24h_vol"),
        }
    except Exception:
        return None


def get_latest_price(db: Session, symbol: str) -> MarketPrice | None:
    return db.scalars(
        select(MarketPrice)
        .where(MarketPrice.symbol == symbol.upper())
        .order_by(MarketPrice.created_at.desc(), MarketPrice.id.desc())
        .limit(1)
    ).first()


def sync_price(db: Session, symbol: str) -> MarketPrice | None:
    """Fetch from CMC, then CoinGecko; store and return the snapshot."""
    payload = fetch_price_cmc(symbol) or fetch_price_coingecko(symbol)
    if payload is None:
        return get_latest_price(db, symbol)
    price = MarketPrice(**payload)
    db.add(price)
    db.commit()
    return price


def record_manual_price(db: Session, symbol: str, price: float, change_24h: float | None = None) -> MarketPrice:
    entry = MarketPrice(symbol=symbol.upper(), provider="manual", price=price, change_24h=change_24h)
    db.add(entry)
    db.commit()
    return entry


def revalue_holdings(db: Session, user_id: int) -> int:
    """Update current_price/total_value/unrealized_pnl for all holdings."""
    holdings = db.scalars(
        select(CryptoHolding).where(CryptoHolding.user_id == user_id)
    ).all()
    updated = 0
    for holding in holdings:
        latest = get_latest_price(db, holding.symbol)
        if latest is None:
            continue
        holding.current_price = latest.price
        holding.total_value = round(holding.amount * latest.price, 2)
        if holding.average_buy_price:
            holding.unrealized_pnl = round(
                (latest.price - holding.average_buy_price) * holding.amount, 2
            )
        holding.last_sync_at = datetime.utcnow()
        updated += 1
    db.commit()
    return updated
