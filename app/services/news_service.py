"""News / risk feed — architecture-ready stub.

Real providers (crypto news, macro, Fed, ETF flows, hack/exploit alerts,
delistings, withdrawal pauses, token unlocks) plug in later behind the same
NewsItem shape. For now items come from manual input or the in-memory mock.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsItem:
    title: str
    summary: str = ""
    # crypto, macro, fed, etf, exchange_risk, hack, delisting, withdrawal_pause,
    # network_outage, token_unlock
    category: str = "crypto"
    severity: str = "low"  # low / medium / high
    related_symbols: list[str] = field(default_factory=list)
    source: str = "manual"
    published_at: datetime = field(default_factory=datetime.utcnow)


# In-memory store for manually added items (replace with DB/provider later).
_manual_items: list[NewsItem] = []


def add_manual_news(item: NewsItem) -> None:
    _manual_items.append(item)


def clear_manual_news() -> None:
    _manual_items.clear()


def fetch_news() -> list[NewsItem]:
    """Return current news items. Provider integrations slot in here."""
    return list(_manual_items)


def match_news_to_portfolio(items: list[NewsItem], portfolio_symbols: set[str]) -> list[tuple[NewsItem, list[str]]]:
    """Pair each news item with the user's affected symbols (if any)."""
    matches = []
    upper = {s.upper() for s in portfolio_symbols}
    for item in items:
        affected = [s for s in item.related_symbols if s.upper() in upper]
        if affected:
            matches.append((item, affected))
    return matches


def urgent_risks(items: list[NewsItem]) -> list[NewsItem]:
    return [i for i in items if i.severity == "high"]
