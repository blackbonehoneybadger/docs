"""Crypto models: exchange connections, holdings, cold wallets."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.core import TimestampMixin


class ExchangeConnection(Base, TimestampMixin):
    __tablename__ = "exchange_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    exchange_name: Mapped[str] = mapped_column(String(64))
    encrypted_api_key: Mapped[str | None] = mapped_column(Text)
    encrypted_api_secret: Mapped[str | None] = mapped_column(Text)
    encrypted_passphrase: Mapped[str | None] = mapped_column(Text)
    permissions_detected: Mapped[str | None] = mapped_column(String(255))
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)


class CryptoHolding(Base, TimestampMixin):
    __tablename__ = "crypto_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    source_id: Mapped[int | None] = mapped_column(ForeignKey("connected_sources.id"))
    exchange_name: Mapped[str | None] = mapped_column(String(64))
    wallet_name: Mapped[str | None] = mapped_column(String(120))
    chain: Mapped[str | None] = mapped_column(String(32))
    symbol: Mapped[str] = mapped_column(String(32))
    token_name: Mapped[str | None] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    average_buy_price: Mapped[float | None] = mapped_column(Float)
    current_price: Mapped[float | None] = mapped_column(Float)
    total_value: Mapped[float | None] = mapped_column(Float)
    unrealized_pnl: Mapped[float | None] = mapped_column(Float)
    staking: Mapped[bool] = mapped_column(Boolean, default=False)
    staking_apy: Mapped[float | None] = mapped_column(Float)
    # exchange, cold_wallet, hot_wallet, manual
    location: Mapped[str] = mapped_column(String(32), default="manual")
    risk_level: Mapped[str | None] = mapped_column(String(16))
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)


class Wallet(Base, TimestampMixin):
    """Cold wallet tracked by PUBLIC address only. Never store keys or seeds."""

    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    wallet_name: Mapped[str] = mapped_column(String(120))
    # BTC, Ethereum, Solana, Polygon, Arbitrum, Base, BNB Chain, Avalanche
    chain: Mapped[str] = mapped_column(String(32))
    public_address: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)
