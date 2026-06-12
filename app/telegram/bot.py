"""Telegram bot: long-polling command loop.

Run with:  python -m app.telegram.bot

Implements the command set from the spec. Free-form sensitive input
(seed phrases / private keys) is rejected and never stored.
"""

import time
from datetime import date, datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.cfo_agent import CfoAgent
from app.agents.crypto_agent import CryptoAgent
from app.agents.market_agent import MarketAgent
from app.agents.accountant_agent import AccountantAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.risk_agent import RiskAgent
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models import (
    CashEntry,
    ConnectedSource,
    CryptoHolding,
    ExchangeConnection,
    FinancialAccount,
    InvestmentRecommendation,
    TradingViewSignal,
    UpcomingObligation,
    User,
    Wallet,
)
from app.reports.daily_report import build_daily_bundle
from app.security.api_key_validator import validate_sensitive_input
from app.security.audit_log import log_event
from app.telegram.notify import send_telegram_document, send_telegram_message, send_telegram_photo

API = "https://api.telegram.org"

HELP_TEXT = """Команды Badger CFO:
/sources — подключенные источники
/connect_bank — как подключить банк (Plaid)
/sync_all — синхронизировать всё
/add_cash_income <сумма> <описание> — наличный доход
/add_cash_expense <сумма> <описание> — наличный расход
/add_card <имя> <лимит> <баланс> — карта вручную
/add_exchange <название> — биржа (read-only)
/add_wallet <имя> <chain> <публичный адрес> — холодный кошелёк
/portfolio — портфель
/banks — банки и карты
/debts — долги
/obligations — ближайшие платежи
/today_plan — план на сегодня
/morning_report — утренний отчёт (+PDF, +картинка)
/evening_report — вечерний отчёт
/pdf_today — PDF за сегодня
/image_today — картинка-сводка
/recommend — инвестиционная рекомендация
/risk — риски сегодня
/alerts — активные предупреждения"""


def _get_user(db: Session, chat_id: str) -> User:
    user = db.scalars(select(User).where(User.telegram_chat_id == chat_id)).first()
    if user is None:
        user = db.scalars(select(User).where(User.telegram_chat_id.is_(None))).first()
        if user is not None:
            user.telegram_chat_id = chat_id
        else:
            user = User(telegram_chat_id=chat_id)
            db.add(user)
        db.commit()
        db.refresh(user)
    return user


def handle_command(db: Session, user: User, text: str) -> str:
    """Route one message; returns the reply text."""
    guard = validate_sensitive_input(text)
    if not guard.ok:
        log_event(db, "security", "sensitive_input_rejected", user_id=user.id, actor="telegram")
        return guard.reason

    parts = text.strip().split()
    cmd = parts[0].split("@")[0].lower() if parts else ""
    args = parts[1:]

    log_event(db, "command", cmd or "(empty)", user_id=user.id, actor="telegram")

    if cmd in ("/start", "/help"):
        return HELP_TEXT

    if cmd == "/sources":
        rows = db.scalars(select(ConnectedSource).where(ConnectedSource.user_id == user.id)).all()
        if not rows:
            return "Источники не подключены. /connect_bank, /add_exchange, /add_wallet, /add_card."
        return "Источники:\n" + "\n".join(
            f"- {s.display_name}: {s.status} ({s.source_type}, {'read-only' if s.read_only else '!!'})"
            for s in rows
        )

    if cmd == "/connect_bank":
        return ("Подключение банка через Plaid (read-only):\n"
                "1. Запусти API: uvicorn app.main:app\n"
                "2. POST /plaid/create_link_token — получи link_token\n"
                "3. Пройди Plaid Link в браузере, получи public_token\n"
                "4. POST /plaid/exchange_public_token\n"
                "5. POST /plaid/sync\n"
                "Подробно: docs/PLAID_SANDBOX.md")

    if cmd == "/sync_all":
        from app.services import market_service
        for symbol in ("BTC", "ETH", "SOL"):
            market_service.sync_price(db, symbol)
        updated = market_service.revalue_holdings(db, user.id)
        return f"Синхронизация выполнена. Обновлено позиций: {updated}."

    if cmd in ("/add_cash_income", "/add_cash_expense"):
        if not args:
            return f"Формат: {cmd} 300 работа"
        try:
            amount = float(args[0])
        except ValueError:
            return f"Не понял сумму '{args[0]}'. Формат: {cmd} 300 работа"
        entry_type = "cash_income" if cmd == "/add_cash_income" else "cash_expense"
        db.add(CashEntry(user_id=user.id, amount=abs(amount), type=entry_type,
                         description=" ".join(args[1:]) or None))
        db.commit()
        verb = "Доход" if entry_type == "cash_income" else "Расход"
        return f"{verb} ${abs(amount):,.2f} записан."

    if cmd == "/add_card":
        if len(args) < 3:
            return "Формат: /add_card CreditOne 300 120  (имя, лимит, баланс)"
        try:
            limit, balance = float(args[-2]), float(args[-1])
        except ValueError:
            return "Лимит и баланс должны быть числами. Формат: /add_card CreditOne 300 120"
        name = " ".join(args[:-2])
        db.add(FinancialAccount(user_id=user.id, name=name, account_type="credit_card",
                                credit_limit=limit, current_balance=balance,
                                external_source="manual"))
        db.commit()
        return f"Карта {name} добавлена: лимит ${limit:,.2f}, баланс ${balance:,.2f}."

    if cmd == "/add_exchange":
        if not args:
            return "Формат: /add_exchange Bybit\nAPI-ключи (только read-only!) добавляются через POST /exchanges/add."
        name = args[0]
        db.add(ExchangeConnection(user_id=user.id, exchange_name=name.lower(),
                                  permissions_detected="manual", read_only=True))
        db.add(ConnectedSource(user_id=user.id, source_type="exchange",
                               provider_name=name.lower(), display_name=name.title(),
                               read_only=True))
        db.commit()
        return (f"Биржа {name.title()} добавлена как manual source.\n"
                "Для API-синка добавь read-only ключ через POST /exchanges/add — "
                "ключи с trade/withdraw будут отклонены.")

    if cmd == "/add_wallet":
        if len(args) < 3:
            return "Формат: /add_wallet ColdWallet1 Solana <публичный_адрес>\nНикогда не присылай seed phrase!"
        wallet_name, chain, address = args[0], args[1], args[2]
        db.add(Wallet(user_id=user.id, wallet_name=wallet_name, chain=chain,
                      public_address=address))
        db.add(ConnectedSource(user_id=user.id, source_type="wallet",
                               provider_name=chain.lower(), display_name=wallet_name,
                               read_only=True))
        db.commit()
        return f"Кошелёк {wallet_name} ({chain}) добавлен. Отслеживаю только публичный адрес."

    if cmd == "/portfolio":
        return CryptoAgent().render_portfolio(db, user.id)

    if cmd == "/banks":
        return AccountantAgent().render_banks(db, user.id)

    if cmd == "/debts":
        accounts = db.scalars(select(FinancialAccount).where(
            FinancialAccount.user_id == user.id,
            FinancialAccount.account_type.in_(("credit_card", "loan")))).all()
        if not accounts:
            return "Долгов не записано."
        total = sum(a.current_balance for a in accounts)
        lines = ["Долги:"]
        for a in accounts:
            lines.append(f"- {a.name}: ${a.current_balance:,.2f}"
                         + (f" / лимит ${a.credit_limit:,.2f}" if a.credit_limit else ""))
        lines.append(f"Всего: ${total:,.2f}")
        return "\n".join(lines)

    if cmd == "/obligations":
        return AccountantAgent().render_obligations(db, user.id)

    if cmd == "/today_plan":
        summary = CfoAgent().analyze(db, user)
        return CfoAgent().render_cashflow(summary)

    if cmd in ("/morning_report", "/evening_report"):
        greeting = "Доброе утро" if cmd == "/morning_report" else "Добрый вечер"
        bundle = build_daily_bundle(db, user, greeting=greeting)
        send_telegram_message(bundle.text, chat_id=user.telegram_chat_id)
        send_telegram_document(bundle.pdf_path, chat_id=user.telegram_chat_id, caption="PDF report")
        send_telegram_photo(bundle.image_path, chat_id=user.telegram_chat_id, caption="Summary")
        return ""  # already sent

    if cmd == "/pdf_today":
        bundle = build_daily_bundle(db, user)
        send_telegram_document(bundle.pdf_path, chat_id=user.telegram_chat_id, caption="PDF report")
        return ""

    if cmd == "/image_today":
        bundle = build_daily_bundle(db, user)
        send_telegram_photo(bundle.image_path, chat_id=user.telegram_chat_id, caption="Summary")
        return ""

    if cmd == "/recommend":
        summary = CfoAgent().analyze(db, user)
        text_out, _ = OrchestratorAgent().build_daily_recommendation(db, user, summary)
        return text_out

    if cmd == "/risk":
        summary = CfoAgent().analyze(db, user)
        return RiskAgent().render_risks(summary)

    if cmd == "/alerts":
        cutoff = datetime.utcnow() - timedelta(days=2)
        signals = db.scalars(select(TradingViewSignal)
                             .where(TradingViewSignal.created_at >= cutoff)
                             .order_by(TradingViewSignal.created_at.desc())).all()
        pending = db.scalars(select(InvestmentRecommendation).where(
            InvestmentRecommendation.user_id == user.id,
            InvestmentRecommendation.status == "proposed",
            InvestmentRecommendation.recommendation_date >= date.today() - timedelta(days=2),
        )).all()
        lines = ["Активные предупреждения:"]
        for s in signals:
            lines.append(f"- TV: {s.symbol} {s.signal} ({s.risk_note})")
        for r in pending:
            lines.append(f"- Рекомендация #{r.id}: {r.recommendation_type} {r.symbol} "
                         f"${r.amount_suggested or 0:,.2f} — ждёт решения")
        if len(lines) == 1:
            lines.append("- Нет активных предупреждений.")
        return "\n".join(lines)

    return "Не понял команду. /help — список команд."


def run_polling() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN не задан в .env")
    init_db()
    offset = 0
    print("Badger CFO bot: polling started")
    while True:
        try:
            resp = httpx.get(
                f"{API}/bot{settings.telegram_bot_token}/getUpdates",
                params={"timeout": 30, "offset": offset},
                timeout=40,
            )
            for update in resp.json().get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                text = message.get("text")
                chat_id = str(message.get("chat", {}).get("id", ""))
                if not text or not chat_id:
                    continue
                with SessionLocal() as db:
                    user = _get_user(db, chat_id)
                    reply = handle_command(db, user, text)
                if reply:
                    send_telegram_message(reply, chat_id=chat_id)
        except KeyboardInterrupt:
            break
        except Exception as exc:  # network hiccups shouldn't kill the loop
            print(f"poll error: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    run_polling()
