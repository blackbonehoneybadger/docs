"""Plaid endpoints (read-only products only)."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import FinancialAccount
from app.services import plaid_service
from app.services.plaid_service import PlaidNotConfiguredError

router = APIRouter(prefix="/plaid", tags=["plaid"])


class PublicTokenIn(BaseModel):
    public_token: str


@router.post("/create_link_token")
def create_link_token(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    try:
        return plaid_service.create_link_token(user.id)
    except PlaidNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/exchange_public_token")
def exchange_public_token(payload: PublicTokenIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    try:
        item = plaid_service.exchange_public_token(db, user.id, payload.public_token)
    except PlaidNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"item_id": item.item_id, "status": item.status}


@router.post("/sync")
def sync(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    try:
        count = plaid_service.sync_accounts(db, user.id)
    except PlaidNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"accounts_synced": count}


@router.get("/accounts")
def accounts(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(FinancialAccount).where(
            FinancialAccount.user_id == user.id,
            FinancialAccount.external_source == "plaid",
        )
    ).all()
    return [
        {"id": a.id, "name": a.name, "type": a.account_type, "mask": a.mask,
         "balance": a.current_balance, "available": a.available_balance,
         "limit": a.credit_limit}
        for a in rows
    ]
