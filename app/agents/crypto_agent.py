"""Crypto Agent: portfolio, drawdowns, allocation, staking, exchange risk."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CryptoHolding, WatchlistAsset
from app.services.market_service import get_latest_price

EXCHANGE_EXPOSURE_WARN = 0.5  # warn when >50% of crypto sits on exchanges


class CryptoAgent:
    name = "crypto"

    def holdings(self, db: Session, user_id: int) -> list[CryptoHolding]:
        return list(
            db.scalars(select(CryptoHolding).where(CryptoHolding.user_id == user_id))
        )

    def total_value(self, holdings: list[CryptoHolding]) -> float:
        return sum(h.total_value or 0.0 for h in holdings)

    def allocation_percent(self, holdings: list[CryptoHolding], symbol: str) -> float:
        total = self.total_value(holdings)
        if total <= 0:
            return 0.0
        value = sum(h.total_value or 0.0 for h in holdings if h.symbol == symbol.upper())
        return value / total * 100

    def exchange_exposure(self, holdings: list[CryptoHolding]) -> float:
        total = self.total_value(holdings)
        if total <= 0:
            return 0.0
        on_exchange = sum(
            h.total_value or 0.0 for h in holdings if h.location == "exchange"
        )
        return on_exchange / total

    def suggest_action(self, db: Session, user_id: int, holding: CryptoHolding) -> str:
        """hold / consider buy / reduce risk — explained, never imperative."""
        latest = get_latest_price(db, holding.symbol)
        watch = db.scalars(
            select(WatchlistAsset).where(
                WatchlistAsset.user_id == user_id,
                WatchlistAsset.symbol == holding.symbol,
            )
        ).first()
        if latest is None:
            return "hold (данных недостаточно)"
        if watch and watch.max_allocation_percent is not None:
            alloc = self.allocation_percent(self.holdings(db, user_id), holding.symbol)
            if alloc >= watch.max_allocation_percent:
                return "reduce risk (превышен max allocation)"
        if watch and watch.buy_zone_price and latest.price <= watch.buy_zone_price:
            return "consider buy (цена в buy zone)"
        if (latest.change_24h or 0) < -10:
            return "watch (резкая просадка за 24ч)"
        return "hold"

    def render_portfolio(self, db: Session, user_id: int) -> str:
        holdings = self.holdings(db, user_id)
        lines = ["5. Крипто портфель", "", f"Total crypto: ${self.total_value(holdings):,.2f}", ""]
        if not holdings:
            lines.append("Портфель пуст. Добавь активы через /add_exchange или /add_wallet.")
        for h in holdings:
            latest = get_latest_price(db, h.symbol)
            change = f"{latest.change_24h:+.1f}%" if latest and latest.change_24h is not None else "n/a"
            lines += [
                f"{h.symbol}:",
                f"- Amount: {h.amount}",
                f"- Value: ${h.total_value or 0:,.2f}",
                f"- 24h: {change}",
                f"- Location: {h.location}",
                f"- Action: {self.suggest_action(db, user_id, h)}",
                "",
            ]
        exposure = self.exchange_exposure(holdings)
        if exposure > EXCHANGE_EXPOSURE_WARN:
            lines.append(
                f"Security note: {exposure * 100:.0f}% крипты лежит на биржах. "
                "Не хранить крупные суммы на бирже без причины — рассмотри cold wallet."
            )
        return "\n".join(lines).rstrip()
