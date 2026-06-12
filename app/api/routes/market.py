"""Market data endpoints: prices and watchlist."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import WatchlistAsset
from app.services import market_service

router = APIRouter(prefix="/market", tags=["market"])


class WatchlistIn(BaseModel):
    symbol: str
    name: str | None = None
    target_allocation_percent: float | None = None
    max_allocation_percent: float | None = None
    buy_zone_price: float | None = None
    strong_buy_zone_price: float | None = None
    notes: str | None = None


class ManualPriceIn(BaseModel):
    symbol: str
    price: float
    change_24h: float | None = None


@router.get("/prices")
def prices(symbols: str = "BTC,ETH,SOL", db: Session = Depends(get_db)):
    result = {}
    for symbol in symbols.split(","):
        latest = market_service.get_latest_price(db, symbol.strip())
        result[symbol.strip().upper()] = (
            {"price": latest.price, "change_24h": latest.change_24h,
             "provider": latest.provider, "as_of": latest.created_at}
            if latest else None
        )
    return result


@router.post("/prices/sync")
def sync_prices(symbols: str = "BTC,ETH,SOL", db: Session = Depends(get_db)):
    synced = []
    for symbol in symbols.split(","):
        price = market_service.sync_price(db, symbol.strip())
        if price:
            synced.append(price.symbol)
    return {"synced": synced}


@router.post("/prices/manual")
def manual_price(payload: ManualPriceIn, db: Session = Depends(get_db)):
    entry = market_service.record_manual_price(db, payload.symbol, payload.price, payload.change_24h)
    return {"id": entry.id, "symbol": entry.symbol, "price": entry.price}


@router.get("/watchlist")
def watchlist(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(WatchlistAsset).where(WatchlistAsset.user_id == user.id)
    ).all()
    return [
        {"id": w.id, "symbol": w.symbol, "name": w.name,
         "target_allocation_percent": w.target_allocation_percent,
         "max_allocation_percent": w.max_allocation_percent,
         "buy_zone_price": w.buy_zone_price,
         "strong_buy_zone_price": w.strong_buy_zone_price}
        for w in rows
    ]


@router.post("/watchlist")
def add_watchlist(payload: WatchlistIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    asset = WatchlistAsset(user_id=user.id, **payload.model_dump())
    asset.symbol = asset.symbol.upper()
    db.add(asset)
    db.commit()
    return {"id": asset.id, "status": "created"}
