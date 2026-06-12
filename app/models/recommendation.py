"""Investment recommendations — always proposals, never executions."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InvestmentRecommendation(Base):
    __tablename__ = "investment_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recommendation_date: Mapped[date] = mapped_column(Date, default=date.today)
    # buy_more, hold, reduce_risk, move_to_cold_wallet, avoid, watch
    recommendation_type: Mapped[str] = mapped_column(String(32))
    symbol: Mapped[str | None] = mapped_column(String(32))
    amount_suggested: Mapped[float | None] = mapped_column(Float)
    reason: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(String(16))
    confidence: Mapped[str | None] = mapped_column(String(16))
    requires_user_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    # proposed, approved, rejected, expired
    status: Mapped[str] = mapped_column(String(16), default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
