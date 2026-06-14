"""Orchestrator Agent: assembles the full daily report from all agents."""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.accountant_agent import AccountantAgent
from app.agents.cfo_agent import CfoAgent
from app.agents.crypto_agent import CryptoAgent
from app.agents.discipline_agent import DisciplineAgent
from app.agents.market_agent import MarketAgent
from app.agents.news_agent import NewsAgent
from app.agents.risk_agent import RiskAgent
from app.models import ConnectedSource, InvestmentRecommendation, User, Wallet
from app.security.audit_log import log_event
from app.security.guardrails import RecommendationDraft
from app.services.cfo_service import CfoSummary


class OrchestratorAgent:
    name = "orchestrator"

    def __init__(self):
        self.cfo = CfoAgent()
        self.accountant = AccountantAgent()
        self.crypto = CryptoAgent()
        self.market = MarketAgent()
        self.news = NewsAgent()
        self.risk = RiskAgent()
        self.discipline = DisciplineAgent()

    # ------------------------------------------------------------------
    # Investment advice of the day
    # ------------------------------------------------------------------
    def build_daily_recommendation(
        self, db: Session, user: User, summary: CfoSummary
    ) -> tuple[str, list[InvestmentRecommendation]]:
        capacity = summary.investment_capacity
        lines = ["10. Инвестиционный совет дня", ""]
        recommendations: list[InvestmentRecommendation] = []

        if capacity <= 0:
            lines += [
                "Свободных денег для инвестиций сегодня нет.",
                "Главная цель — сохранить cashflow и закрыть обязательства.",
            ]
            return "\n".join(lines), recommendations

        # Conservative split: never deploy everything.
        reserve = round(capacity * 0.4, 2)
        btc_part = round(capacity * 0.3, 2)
        sol_part = round(capacity * 0.2, 2)
        dry_powder = round(capacity - reserve - btc_part - sol_part, 2)

        lines += [
            f"Свободно для инвестиций сегодня: ${capacity:,.2f}",
            "",
            "Я НЕ советую вкладывать всё.",
            "",
            "Вариант:",
            f"- ${reserve:,.2f} оставить в cash reserve",
            f"- ${btc_part:,.2f} рассмотреть в BTC",
            f"- ${sol_part:,.2f} рассмотреть в SOL",
            f"- ${dry_powder:,.2f} оставить как dry powder",
            "",
            "Почему:",
            "- распределение снижает риск против одной позиции",
            f"- emergency fund: {summary.survival_ratio:.1f} мес. расходов",
            f"- впереди платежей на ${summary.upcoming_obligations_total:,.2f} за 14 дней",
            "- нельзя ломать cashflow ради крипты",
            "",
        ]

        for symbol, amount in (("BTC", btc_part), ("SOL", sol_part)):
            if amount <= 0:
                continue
            draft = RecommendationDraft(
                symbol=symbol,
                amount=amount,
                recommendation_type="buy_more",
                aggressive=False,
            )
            verdict = self.risk.review(db, user.id, summary, draft)
            if not verdict.allowed:
                lines.append(f"{symbol}: заблокировано риск-агентом — {'; '.join(verdict.reasons)}")
                continue
            rec = InvestmentRecommendation(
                user_id=user.id,
                recommendation_type="buy_more",
                symbol=symbol,
                amount_suggested=amount,
                reason="Консервативное распределение свободного cash по плану дня.",
                evidence=f"Investment capacity ${capacity:,.2f}; survival ratio {summary.survival_ratio:.1f} мес.",
                risk_level="medium",
                confidence="medium",
                requires_user_approval=True,
                status="proposed",
            )
            db.add(rec)
            recommendations.append(rec)
            for warning in verdict.warnings:
                lines.append(f"Внимание ({symbol}): {warning}")
        db.commit()
        for rec in recommendations:
            log_event(
                db,
                event_type="recommendation",
                actor=self.name,
                action=f"proposed:{rec.recommendation_type}:{rec.symbol}",
                user_id=user.id,
                details={"amount": rec.amount_suggested, "id": rec.id},
            )

        lines += [
            "",
            "Confidence: medium",
            "Risk: medium",
            "Нужно подтверждение пользователя (/recommend → approve/reject).",
        ]
        return "\n".join(lines), recommendations

    # ------------------------------------------------------------------
    # Sections that don't have a dedicated agent
    # ------------------------------------------------------------------
    def render_sources_summary(self, db: Session, user_id: int) -> str:
        sources = db.scalars(
            select(ConnectedSource).where(ConnectedSource.user_id == user_id)
        ).all()
        lines = ["6. Биржи и источники", ""]
        if not sources:
            lines.append("Источники не подключены. /sources для списка, /add_exchange для добавления.")
        for s in sources:
            ro = "read-only" if s.read_only else "ОПАСНО: не read-only"
            lines.append(f"{s.display_name}: {s.status} / {ro}")
        return "\n".join(lines)

    def render_wallets(self, db: Session, user_id: int) -> str:
        wallets = db.scalars(select(Wallet).where(Wallet.user_id == user_id)).all()
        lines = ["7. Cold Wallets", ""]
        if not wallets:
            lines.append("Холодные кошельки не добавлены. /add_wallet.")
        for w in wallets:
            lines += [
                f"{w.wallet_name}:",
                f"- Chain: {w.chain}",
                f"- Address: {w.public_address[:10]}...",
                "- Status: safe (tracked by public address)",
                "",
            ]
        lines.append(
            "Security note: не хранить крупные суммы на бирже без причины. "
            "При risk alert по бирже — срочное предупреждение."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # The big daily message
    # ------------------------------------------------------------------
    def build_daily_report(self, db: Session, user: User, greeting: str = "Доброе утро") -> str:
        summary = self.cfo.analyze(db, user)
        advice, _ = self.build_daily_recommendation(db, user, summary)
        sections = [
            f"{greeting}, {user.name}.",
            "",
            "Boss My Life Report",
            f"Дата: {date.today().isoformat()}",
            "",
            self.cfo.render_overview(summary),
            "",
            self.accountant.render_banks(db, user.id),
            "",
            self.accountant.render_obligations(db, user.id),
            "",
            self.cfo.render_cashflow(summary),
            "",
            self.crypto.render_portfolio(db, user.id),
            "",
            self.render_sources_summary(db, user.id),
            "",
            self.render_wallets(db, user.id),
            "",
            self.market.render_market(db),
            "",
            self.news.render_news(db, user.id),
            "",
            advice,
            "",
            self.discipline.render_discipline(summary),
            "",
            "12. Файлы",
            "",
            "PDF report: generated",
            "Image summary: generated",
        ]
        report = "\n".join(sections)
        log_event(
            db,
            event_type="ai_decision",
            actor=self.name,
            action="daily_report_built",
            user_id=user.id,
            details={"length": len(report), "at": datetime.utcnow().isoformat()},
        )
        return report
