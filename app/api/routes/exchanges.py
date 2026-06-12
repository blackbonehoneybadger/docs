"""Exchange connections (read-only keys only) and holdings."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters import get_adapter
from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import ConnectedSource, CryptoHolding, ExchangeConnection
from app.security.audit_log import log_event
from app.security.encryption import decrypt_secret, encrypt_secret

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


class ExchangeIn(BaseModel):
    exchange_name: str
    api_key: str | None = None
    api_secret: str | None = None
    passphrase: str | None = None


class ManualHoldingIn(BaseModel):
    exchange_name: str | None = None
    wallet_name: str | None = None
    symbol: str
    amount: float
    average_buy_price: float | None = None
    location: str = "manual"
    staking: bool = False


@router.post("/add")
def add_exchange(payload: ExchangeIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)

    permissions = "manual"
    if payload.api_key:
        try:
            adapter = get_adapter(
                payload.exchange_name,
                api_key=payload.api_key,
                api_secret=payload.api_secret or "",
                passphrase=payload.passphrase or "",
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        verdict = adapter.validate_read_only()
        if not verdict.ok:
            log_event(db, "security", "exchange_key_rejected", user_id=user.id,
                      details={"exchange": payload.exchange_name, "reason": verdict.reason})
            raise HTTPException(status_code=400, detail=verdict.reason)
        permissions = ",".join(adapter.detect_permissions()) or "unknown"

    connection = ExchangeConnection(
        user_id=user.id,
        exchange_name=payload.exchange_name.lower(),
        encrypted_api_key=encrypt_secret(payload.api_key) if payload.api_key else None,
        encrypted_api_secret=encrypt_secret(payload.api_secret) if payload.api_secret else None,
        encrypted_passphrase=encrypt_secret(payload.passphrase) if payload.passphrase else None,
        permissions_detected=permissions,
        read_only=True,
    )
    db.add(connection)
    db.add(
        ConnectedSource(
            user_id=user.id,
            source_type="exchange",
            provider_name=payload.exchange_name.lower(),
            display_name=payload.exchange_name.title(),
            read_only=True,
        )
    )
    db.commit()
    log_event(db, "sync", "exchange_added", user_id=user.id,
              details={"exchange": payload.exchange_name})
    return {"id": connection.id, "permissions_detected": permissions}


@router.post("/sync")
def sync_exchanges(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    connections = db.scalars(
        select(ExchangeConnection).where(ExchangeConnection.user_id == user.id)
    ).all()
    synced = 0
    for conn in connections:
        if not conn.encrypted_api_key:
            continue
        try:
            adapter = get_adapter(
                conn.exchange_name,
                api_key=decrypt_secret(conn.encrypted_api_key),
                api_secret=decrypt_secret(conn.encrypted_api_secret) if conn.encrypted_api_secret else "",
            )
        except ValueError:
            continue
        for balance in adapter.fetch_balances():
            holding = db.scalars(
                select(CryptoHolding).where(
                    CryptoHolding.user_id == user.id,
                    CryptoHolding.exchange_name == conn.exchange_name,
                    CryptoHolding.symbol == balance.symbol.upper(),
                )
            ).first()
            if holding is None:
                holding = CryptoHolding(
                    user_id=user.id,
                    exchange_name=conn.exchange_name,
                    symbol=balance.symbol.upper(),
                    location="exchange",
                )
                db.add(holding)
            holding.amount = balance.amount
            if balance.usd_value:
                holding.total_value = balance.usd_value
            holding.last_sync_at = datetime.utcnow()
            synced += 1
        conn.last_sync_at = datetime.utcnow()
    db.commit()
    log_event(db, "sync", "exchanges_synced", user_id=user.id, details={"holdings": synced})
    return {"holdings_synced": synced}


@router.get("")
def list_exchanges(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(ExchangeConnection).where(ExchangeConnection.user_id == user.id)
    ).all()
    # Secrets are never returned.
    return [
        {"id": c.id, "exchange_name": c.exchange_name, "status": c.status,
         "read_only": c.read_only, "permissions_detected": c.permissions_detected,
         "last_sync_at": c.last_sync_at}
        for c in rows
    ]


@router.get("/holdings")
def list_holdings(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(CryptoHolding).where(CryptoHolding.user_id == user.id)
    ).all()
    return [
        {"id": h.id, "symbol": h.symbol, "amount": h.amount, "location": h.location,
         "exchange": h.exchange_name, "wallet": h.wallet_name,
         "current_price": h.current_price, "total_value": h.total_value,
         "unrealized_pnl": h.unrealized_pnl, "staking": h.staking}
        for h in rows
    ]


@router.post("/holdings/manual")
def add_manual_holding(payload: ManualHoldingIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    holding = CryptoHolding(
        user_id=user.id,
        symbol=payload.symbol.upper(),
        amount=payload.amount,
        average_buy_price=payload.average_buy_price,
        exchange_name=payload.exchange_name,
        wallet_name=payload.wallet_name,
        location=payload.location,
        staking=payload.staking,
    )
    db.add(holding)
    db.commit()
    return {"id": holding.id, "status": "created"}
