"""News Agent: collects news, maps them onto the user's portfolio."""

from sqlalchemy.orm import Session

from app.agents.crypto_agent import CryptoAgent
from app.services import news_service


class NewsAgent:
    name = "news"

    def render_news(self, db: Session, user_id: int) -> str:
        items = news_service.fetch_news()
        lines = ["9. Новости и риски", ""]
        if not items:
            lines.append("Свежих новостей нет (источники ещё не подключены или лента пуста).")
            return "\n".join(lines)

        for item in items[:5]:
            lines.append(f"- [{item.severity}] {item.title}")

        symbols = {h.symbol for h in CryptoAgent().holdings(db, user_id)}
        matches = news_service.match_news_to_portfolio(items, symbols)
        if matches:
            lines.append("")
            for item, affected in matches:
                for sym in affected:
                    lines.append(
                        f"У тебя есть {sym}. Новость влияет на {sym}. Риск: {item.severity}. "
                        "Действие: проверить, держать ли на бирже или перевести на cold wallet."
                    )
        return "\n".join(lines)
