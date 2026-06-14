"""Daily report scheduler.

Run with:  python -m app.scheduler

Sends the morning and evening reports to Telegram at the configured local
times (REPORT_TIMEZONE, MORNING_REPORT_TIME, EVENING_REPORT_TIME).
"""

import time
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models import User
from app.reports.daily_report import build_daily_bundle
from app.telegram.notify import send_telegram_document, send_telegram_message, send_telegram_photo


def _send_report(greeting: str) -> None:
    with SessionLocal() as db:
        users = db.scalars(select(User).where(User.telegram_chat_id.is_not(None))).all()
        for user in users:
            bundle = build_daily_bundle(db, user, greeting=greeting)
            send_telegram_message(bundle.text, chat_id=user.telegram_chat_id)
            send_telegram_document(bundle.pdf_path, chat_id=user.telegram_chat_id, caption="PDF report")
            send_telegram_photo(bundle.image_path, chat_id=user.telegram_chat_id, caption="Summary")


def run_scheduler() -> None:
    settings = get_settings()
    tz = ZoneInfo(settings.report_timezone)
    sent_today: dict[str, str] = {}  # slot -> date string
    print("Badger CFO scheduler started")
    while True:
        now = datetime.now(tz)
        hhmm = now.strftime("%H:%M")
        today = now.date().isoformat()
        slots = {
            "morning": (settings.morning_report_time, "Доброе утро"),
            "evening": (settings.evening_report_time, "Добрый вечер"),
        }
        for slot, (slot_time, greeting) in slots.items():
            if hhmm == slot_time and sent_today.get(slot) != today:
                _send_report(greeting)
                sent_today[slot] = today
        time.sleep(30)


if __name__ == "__main__":
    init_db()
    run_scheduler()
