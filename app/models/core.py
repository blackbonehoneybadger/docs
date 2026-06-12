"""Core financial models: users, sources, accounts, cash, obligations, snapshots."""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120), default="Badger")
    monthly_expenses_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_passive_income: Mapped[float] = mapped_column(Float, default=0.0)
    emergency_buffer: Mapped[float] = mapped_column(Float, default=200.0)


class ConnectedSource(Base, TimestampMixin):
    __tablename__ = "connected_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # manual, plaid, exchange, wallet, market, news, tradingview
    source_type: Mapped[str] = mapped_column(String(32))
    provider_name: Mapped[str] = mapped_column(String(120))
    display_name: Mapped[str] = mapped_column(String(120))
    # active, inactive, error, needs_reconnect
    status: Mapped[str] = mapped_column(String(32), default="active")
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime)


class PlaidItem(Base, TimestampMixin):
    __tablename__ = "plaid_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    item_id: Mapped[str] = mapped_column(String(120), unique=True)
    institution_id: Mapped[str | None] = mapped_column(String(120))
    institution_name: Mapped[str | None] = mapped_column(String(120))
    encrypted_access_token: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="active")
    last_successful_sync_at: Mapped[datetime | None] = mapped_column(DateTime)


class FinancialAccount(Base, TimestampMixin):
    __tablename__ = "financial_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    source_id: Mapped[int | None] = mapped_column(ForeignKey("connected_sources.id"))
    name: Mapped[str] = mapped_column(String(120))
    institution: Mapped[str | None] = mapped_column(String(120))
    # checking, savings, credit_card, loan, investment, crypto_exchange,
    # wallet, cash, business, other
    account_type: Mapped[str] = mapped_column(String(32))
    subtype: Mapped[str | None] = mapped_column(String(64))
    mask: Mapped[str | None] = mapped_column(String(16))
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    current_balance: Mapped[float] = mapped_column(Float, default=0.0)
    available_balance: Mapped[float | None] = mapped_column(Float)
    credit_limit: Mapped[float | None] = mapped_column(Float)
    minimum_payment: Mapped[float | None] = mapped_column(Float)
    next_due_date: Mapped[date | None] = mapped_column(Date)
    apr: Mapped[float | None] = mapped_column(Float)
    read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    external_id: Mapped[str | None] = mapped_column(String(120))
    external_source: Mapped[str | None] = mapped_column(String(64))
    raw_data: Mapped[dict | None] = mapped_column(JSON)


class Transaction(Base, TimestampMixin):
    """Manual / synced transactions (MVP ledger)."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    account_id: Mapped[int | None] = mapped_column(ForeignKey("financial_accounts.id"))
    amount: Mapped[float] = mapped_column(Float)  # positive = income, negative = expense
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    description: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(64))
    txn_date: Mapped[date] = mapped_column(Date, default=date.today)
    source: Mapped[str] = mapped_column(String(32), default="manual")


class CashEntry(Base):
    __tablename__ = "cash_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    # cash_income, cash_expense, cash_adjustment
    type: Mapped[str] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(String(255))
    category_id: Mapped[str | None] = mapped_column(String(64))
    entry_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UpcomingObligation(Base, TimestampMixin):
    __tablename__ = "upcoming_obligations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    due_date: Mapped[date] = mapped_column(Date)
    # one_time, weekly, biweekly, monthly, yearly
    frequency: Mapped[str] = mapped_column(String(32), default="one_time")
    category: Mapped[str | None] = mapped_column(String(64))
    # manual, plaid, detected
    source: Mapped[str] = mapped_column(String(32), default="manual")
    autopay: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")


class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    snapshot_date: Mapped[date] = mapped_column(Date, default=date.today)
    total_cash: Mapped[float] = mapped_column(Float, default=0.0)
    total_bank: Mapped[float] = mapped_column(Float, default=0.0)
    total_credit_card_debt: Mapped[float] = mapped_column(Float, default=0.0)
    total_crypto: Mapped[float] = mapped_column(Float, default=0.0)
    total_investments: Mapped[float] = mapped_column(Float, default=0.0)
    total_assets: Mapped[float] = mapped_column(Float, default=0.0)
    total_liabilities: Mapped[float] = mapped_column(Float, default=0.0)
    net_worth: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_expenses_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    passive_income: Mapped[float] = mapped_column(Float, default=0.0)
    freedom_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    survival_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    today_free_cash: Mapped[float] = mapped_column(Float, default=0.0)
    personal_spending_allowance: Mapped[float] = mapped_column(Float, default=0.0)
    investment_capacity: Mapped[float] = mapped_column(Float, default=0.0)
    pdf_path: Mapped[str | None] = mapped_column(String(255))
    image_path: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
