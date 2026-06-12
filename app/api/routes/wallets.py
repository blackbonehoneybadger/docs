"""Cold wallets: public address tracking only. Seeds/private keys rejected."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import ConnectedSource, Wallet
from app.security.api_key_validator import validate_sensitive_input
from app.security.audit_log import log_event

router = APIRouter(prefix="/wallets", tags=["wallets"])

SUPPORTED_CHAINS = {
    "BTC", "Ethereum", "Solana", "Polygon", "Arbitrum", "Base", "BNB Chain", "Avalanche",
}


class WalletIn(BaseModel):
    wallet_name: str
    chain: str
    public_address: str
    notes: str | None = None


@router.post("")
def add_wallet(payload: WalletIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)

    for text in (payload.public_address, payload.notes or ""):
        verdict = validate_sensitive_input(text)
        if not verdict.ok:
            log_event(db, "security", "seed_or_key_rejected", user_id=user.id)
            raise HTTPException(status_code=400, detail=verdict.reason)

    wallet = Wallet(
        user_id=user.id,
        wallet_name=payload.wallet_name,
        chain=payload.chain,
        public_address=payload.public_address,
        notes=payload.notes,
    )
    db.add(wallet)
    db.add(
        ConnectedSource(
            user_id=user.id,
            source_type="wallet",
            provider_name=payload.chain.lower(),
            display_name=payload.wallet_name,
            read_only=True,
        )
    )
    db.commit()
    return {"id": wallet.id, "status": "created"}


@router.get("")
def list_wallets(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(select(Wallet).where(Wallet.user_id == user.id)).all()
    return [
        {"id": w.id, "wallet_name": w.wallet_name, "chain": w.chain,
         "public_address": w.public_address, "last_sync_at": w.last_sync_at}
        for w in rows
    ]


@router.post("/sync")
def sync_wallets(db: Session = Depends(get_db)):
    """On-chain balance APIs plug in later; for now this stamps sync time."""
    user = get_or_create_default_user(db)
    rows = db.scalars(select(Wallet).where(Wallet.user_id == user.id)).all()
    for w in rows:
        w.last_sync_at = datetime.utcnow()
    db.commit()
    log_event(db, "sync", "wallets_synced", user_id=user.id, details={"count": len(rows)})
    return {"wallets_synced": len(rows)}
