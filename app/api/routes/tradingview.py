"""TradingView webhook: save -> match portfolio -> risk note -> alert. Never trades."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import CryptoHolding, TradingViewSignal
from app.security.audit_log import log_event
from app.telegram.notify import send_telegram_message

router = APIRouter(prefix="/webhooks", tags=["tradingview"])


class TradingViewAlert(BaseModel):
    symbol: str
    signal: str
    price: float | None = None
    timeframe: str | None = None
    strategy: str | None = None
    confidence: str | None = None


def _base_symbol(pair: str) -> str:
    """SOLUSDT -> SOL, BTCUSD -> BTC."""
    upper = pair.upper()
    for quote in ("USDT", "USDC", "USD", "BUSD", "EUR"):
        if upper.endswith(quote) and len(upper) > len(quote):
            return upper[: -len(quote)]
    return upper


@router.post("/tradingview")
def tradingview_webhook(alert: TradingViewAlert, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    base = _base_symbol(alert.symbol)

    held = db.scalars(
        select(CryptoHolding).where(
            CryptoHolding.user_id == user.id, CryptoHolding.symbol == base
        )
    ).first()

    risk_note = (
        f"Сигнал по активу из портфеля ({base})." if held
        else f"{base} не в портфеле — информационный сигнал."
    )
    signal = TradingViewSignal(
        symbol=alert.symbol.upper(),
        signal=alert.signal.upper(),
        price=alert.price,
        timeframe=alert.timeframe,
        strategy=alert.strategy,
        confidence=alert.confidence,
        matched_portfolio=bool(held),
        risk_note=risk_note,
    )
    db.add(signal)
    db.commit()

    log_event(db, "ai_decision", f"tradingview_signal:{alert.symbol}:{alert.signal}",
              user_id=user.id, details={"matched_portfolio": bool(held)})

    message = (
        f"TradingView сигнал: {alert.symbol} {alert.signal.upper()}"
        f"{f' @ {alert.price}' if alert.price else ''}"
        f" ({alert.timeframe or '?'}, {alert.strategy or '?'}, confidence {alert.confidence or '?'})\n"
        f"{risk_note}\n"
        "Автоматическая покупка ЗАПРЕЩЕНА. Решение за тобой."
    )
    send_telegram_message(message)

    return {"id": signal.id, "matched_portfolio": bool(held), "auto_trade": False}
