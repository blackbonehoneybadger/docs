"""Market data models: prices, watchlist, TradingView signals."""

from datetime import datetime

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.core import TimestampMixin


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    provider: Mapped[str] = mapped_column(String(32), default="manual")
    price: Mapped[float] = mapped_column(Float)
    change_24h: Mapped[float | None] = mapped_column(Float)
    change_7d: Mapped[float | None] = mapped_column(Float)
    change_30d: Mapped[float | None] = mapped_column(Float)
    market_cap: Mapped[float | None] = mapped_column(Float)
    volume_24h: Mapped[float | None] = mapped_column(Float)
    rank: Mapped[int | None] = mapped_column(Integer)
    raw_data: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WatchlistAsset(Base, TimestampMixin):
    __tablename__ = "watchlist_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    symbol: Mapped[str] = mapped_column(String(32))
    name: Mapped[str | None] = mapped_column(String(120))
    target_allocation_percent: Mapped[float | None] = mapped_column(Float)
    max_allocation_percent: Mapped[float | None] = mapped_column(Float)
    buy_zone_price: Mapped[float | None] = mapped_column(Float)
    strong_buy_zone_price: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)


class TradingViewSignal(Base):
    __tablename__ = "tradingview_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32))
    signal: Mapped[str] = mapped_column(String(16))  # BUY / SELL / WATCH
    price: Mapped[float | None] = mapped_column(Float)
    timeframe: Mapped[str | None] = mapped_column(String(16))
    strategy: Mapped[str | None] = mapped_column(String(64))
    confidence: Mapped[str | None] = mapped_column(String(16))
    matched_portfolio: Mapped[bool] = mapped_column(Integer, default=False)
    risk_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
