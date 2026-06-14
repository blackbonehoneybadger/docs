"""Market Agent: prices, TradingView signals, trend snapshot."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TradingViewSignal
from app.services.market_service import get_latest_price, sync_price

CORE_SYMBOLS = ["BTC", "ETH", "SOL"]


class MarketAgent:
    name = "market"

    def sync_core_prices(self, db: Session) -> None:
        for symbol in CORE_SYMBOLS:
            sync_price(db, symbol)

    def recent_signals(self, db: Session, limit: int = 5) -> list[TradingViewSignal]:
        return list(
            db.scalars(
                select(TradingViewSignal)
                .order_by(TradingViewSignal.created_at.desc(), TradingViewSignal.id.desc())
                .limit(limit)
            )
        )

    def macro_risk(self, db: Session) -> str:
        """Crude volatility proxy: big 24h moves on BTC/ETH -> higher risk."""
        worst = 0.0
        for symbol in CORE_SYMBOLS:
            latest = get_latest_price(db, symbol)
            if latest and latest.change_24h is not None:
                worst = max(worst, abs(latest.change_24h))
        if worst >= 8:
            return "high"
        if worst >= 4:
            return "medium"
        return "low"

    def render_market(self, db: Session) -> str:
        lines = ["8. Рынок сегодня", ""]
        have_data = False
        for symbol in CORE_SYMBOLS:
            latest = get_latest_price(db, symbol)
            if latest is None:
                lines.append(f"{symbol}: данных недостаточно")
                continue
            have_data = True
            change = f", 24h {latest.change_24h:+.1f}%" if latest.change_24h is not None else ""
            lines.append(f"{symbol}: ${latest.price:,.2f}{change}")
        lines.append(f"Macro risk: {self.macro_risk(db) if have_data else 'unknown'}")
        signals = self.recent_signals(db, limit=3)
        if signals:
            lines += ["", "TradingView сигналы:"]
            for s in signals:
                lines.append(
                    f"- {s.symbol} {s.signal} @ {s.price} ({s.timeframe}, {s.strategy}, "
                    f"confidence {s.confidence})"
                )
        return "\n".join(lines)
