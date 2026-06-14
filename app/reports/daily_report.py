"""Daily report pipeline: text + PDF + image + snapshot, in one call."""

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.agents.cfo_agent import CfoAgent
from app.agents.market_agent import MarketAgent
from app.agents.orchestrator import OrchestratorAgent
from app.models import User
from app.reports.image_report import generate_image
from app.reports.pdf_report import generate_pdf
from app.services import cfo_service


@dataclass
class DailyReportBundle:
    text: str
    pdf_path: Path
    image_path: Path


def top_actions(summary) -> list[str]:
    actions = []
    if summary.upcoming_obligations_total > summary.available_cash:
        actions.append("Close the cash gap")
    if summary.survival_ratio < 1:
        actions.append("Build emergency fund")
    if summary.investment_capacity > 0:
        actions.append(f"Review invest plan ${summary.investment_capacity:,.0f}")
    if not actions:
        actions.append("Hold the line")
    actions.append("No impulse buys")
    actions.append("Check due dates")
    return actions[:3]


def build_daily_bundle(db: Session, user: User, greeting: str = "Доброе утро") -> DailyReportBundle:
    orchestrator = OrchestratorAgent()
    text = orchestrator.build_daily_report(db, user, greeting=greeting)

    summary = CfoAgent().analyze(db, user)
    risk = MarketAgent().macro_risk(db)
    pdf_path = generate_pdf(text)
    image_path = generate_image(summary, top_actions(summary), risk_level=risk)

    cfo_service.save_snapshot(db, user, summary, pdf_path=str(pdf_path), image_path=str(image_path))
    return DailyReportBundle(text=text, pdf_path=pdf_path, image_path=image_path)
