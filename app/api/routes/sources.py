"""Sources, cash entries, manual accounts, obligations."""

from datetime import date, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import CashEntry, ConnectedSource, FinancialAccount, UpcomingObligation
from app.security.audit_log import log_event
from app.services import market_service

router = APIRouter(tags=["sources"])


class ManualSourceIn(BaseModel):
    source_type: str = "manual"
    provider_name: str
    display_name: str


class ManualAccountIn(BaseModel):
    name: str
    account_type: str
    institution: str | None = None
    current_balance: float = 0.0
    credit_limit: float | None = None
    minimum_payment: float | None = None
    next_due_date: date | None = None


class CashEntryIn(BaseModel):
    amount: float
    type: str  # cash_income / cash_expense / cash_adjustment
    description: str | None = None


class ObligationIn(BaseModel):
    name: str
    amount: float
    due_date: date
    frequency: str = "one_time"
    category: str | None = None
    autopay: bool = False


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    sources = db.scalars(
        select(ConnectedSource).where(ConnectedSource.user_id == user.id)
    ).all()
    return [
        {
            "id": s.id,
            "source_type": s.source_type,
            "provider_name": s.provider_name,
            "display_name": s.display_name,
            "status": s.status,
            "read_only": s.read_only,
            "last_sync_at": s.last_sync_at,
        }
        for s in sources
    ]


@router.post("/sources/manual")
def add_manual_source(payload: ManualSourceIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    source = ConnectedSource(
        user_id=user.id,
        source_type=payload.source_type,
        provider_name=payload.provider_name,
        display_name=payload.display_name,
        read_only=True,
    )
    db.add(source)
    db.commit()
    log_event(db, "sync", "manual_source_added", user_id=user.id,
              details={"display_name": payload.display_name})
    return {"id": source.id, "status": "created"}


@router.post("/sources/sync_all")
def sync_all(db: Session = Depends(get_db)):
    """Refresh market prices and revalue holdings; per-source syncs are additive."""
    user = get_or_create_default_user(db)
    for symbol in ("BTC", "ETH", "SOL"):
        market_service.sync_price(db, symbol)
    updated = market_service.revalue_holdings(db, user.id)
    for source in db.scalars(
        select(ConnectedSource).where(ConnectedSource.user_id == user.id)
    ):
        source.last_sync_at = datetime.utcnow()
    db.commit()
    log_event(db, "sync", "sync_all", user_id=user.id, details={"holdings_updated": updated})
    return {"status": "ok", "holdings_updated": updated}


@router.post("/accounts/manual")
def add_manual_account(payload: ManualAccountIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    account = FinancialAccount(
        user_id=user.id,
        name=payload.name,
        account_type=payload.account_type,
        institution=payload.institution,
        current_balance=payload.current_balance,
        credit_limit=payload.credit_limit,
        minimum_payment=payload.minimum_payment,
        next_due_date=payload.next_due_date,
        external_source="manual",
    )
    db.add(account)
    db.commit()
    return {"id": account.id, "status": "created"}


@router.post("/cash")
def add_cash_entry(payload: CashEntryIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    entry = CashEntry(
        user_id=user.id,
        amount=abs(payload.amount),
        type=payload.type,
        description=payload.description,
    )
    db.add(entry)
    db.commit()
    return {"id": entry.id, "status": "created"}


@router.post("/obligations")
def add_obligation(payload: ObligationIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    obligation = UpcomingObligation(user_id=user.id, **payload.model_dump())
    db.add(obligation)
    db.commit()
    return {"id": obligation.id, "status": "created"}


@router.get("/obligations")
def list_obligations(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(UpcomingObligation)
        .where(UpcomingObligation.user_id == user.id, UpcomingObligation.status == "pending")
        .order_by(UpcomingObligation.due_date)
    ).all()
    return [
        {"id": o.id, "name": o.name, "amount": o.amount, "due_date": o.due_date,
         "frequency": o.frequency, "autopay": o.autopay}
        for o in rows
    ]
