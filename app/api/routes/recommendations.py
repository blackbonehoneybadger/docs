"""Recommendations: list today's proposals; approve/reject (user decision only).

Approving a recommendation changes its status — it does NOT execute anything.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.cfo_agent import CfoAgent
from app.agents.orchestrator import OrchestratorAgent
from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.models import InvestmentRecommendation
from app.security.audit_log import log_event

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/today")
def today(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(InvestmentRecommendation).where(
            InvestmentRecommendation.user_id == user.id,
            InvestmentRecommendation.recommendation_date == date.today(),
        )
    ).all()
    if not rows:
        orchestrator = OrchestratorAgent()
        summary = CfoAgent().analyze(db, user)
        _, rows = orchestrator.build_daily_recommendation(db, user, summary)
    return [
        {"id": r.id, "type": r.recommendation_type, "symbol": r.symbol,
         "amount_suggested": r.amount_suggested, "reason": r.reason,
         "evidence": r.evidence, "risk_level": r.risk_level,
         "confidence": r.confidence, "status": r.status,
         "requires_user_approval": r.requires_user_approval}
        for r in rows
    ]


def _set_status(db: Session, rec_id: int, status: str) -> InvestmentRecommendation:
    rec = db.get(InvestmentRecommendation, rec_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = status
    db.commit()
    log_event(db, "recommendation", f"{status}:{rec.symbol}", user_id=rec.user_id,
              actor="user", details={"id": rec.id})
    return rec


@router.post("/{rec_id}/approve")
def approve(rec_id: int, db: Session = Depends(get_db)):
    rec = _set_status(db, rec_id, "approved")
    return {"id": rec.id, "status": rec.status,
            "note": "Approved as a decision record. Execution is manual — the system never moves money."}


@router.post("/{rec_id}/reject")
def reject(rec_id: int, db: Session = Depends(get_db)):
    rec = _set_status(db, rec_id, "rejected")
    return {"id": rec.id, "status": rec.status}
