# Badger CFO / Boss My Life

Личный финансово-инвестиционный центр в Telegram: банки, кредитки, биржи,
холодные кошельки, обязательные платежи, свободный cashflow и ежедневный
отчёт (текст + PDF + картинка).

**Жёсткие правила безопасности:**

- Никаких переводов денег. Никакой торговли. Никаких withdrawals.
- Private keys и seed phrases НЕ принимаются и НЕ хранятся (бот отклонит их).
- Банковские логины/пароли не хранятся — только Plaid read-only токены.
- Все подключения read-only. Ключи с trade/withdraw правами отклоняются.
- AI proposes, user approves: каждая рекомендация требует подтверждения.

## Быстрый старт (для новичка)

1. Установи Python 3.11+.
2. Склонируй репозиторий и поставь зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Создай файл настроек:

   ```bash
   cp .env.example .env
   ```

4. Сгенерируй ключ шифрования и вставь его в `.env` как `FERNET_KEY`:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

5. Создай Telegram-бота через [@BotFather](https://t.me/BotFather), вставь
   токен в `.env` как `TELEGRAM_BOT_TOKEN`.

6. Запусти API:

   ```bash
   uvicorn app.main:app --reload
   ```

   Swagger-документация: http://localhost:8000/docs

7. Запусти Telegram-бота (в отдельном терминале):

   ```bash
   python -m app.telegram.bot
   ```

8. (Опционально) Запусти планировщик утренних/вечерних отчётов:

   ```bash
   python -m app.scheduler
   ```

9. Напиши боту `/help` — он покажет все команды.

По умолчанию используется SQLite (файл `badger_cfo.db`). Для PostgreSQL
поменяй `DATABASE_URL` в `.env`, например:
`postgresql+psycopg2://user:pass@localhost/badger_cfo`.

## Основные команды бота

| Команда | Что делает |
|---|---|
| `/sources` | Все подключенные источники |
| `/add_cash_income 300 работа` | Наличный доход |
| `/add_cash_expense 50 еда` | Наличный расход |
| `/add_card CreditOne 300 120` | Карта вручную (имя, лимит, баланс) |
| `/add_exchange Bybit` | Биржа (read-only) |
| `/add_wallet Cold1 Solana <адрес>` | Холодный кошелёк (только публичный адрес) |
| `/portfolio` `/banks` `/debts` `/obligations` | Просмотр данных |
| `/today_plan` `/risk` `/alerts` | Cashflow, риски, предупреждения |
| `/morning_report` `/evening_report` | Полный отчёт + PDF + картинка |
| `/recommend` | Инвестиционный совет дня (требует approve) |

## Инструкции

- [Plaid sandbox: подключение банков](docs_project/PLAID_SANDBOX.md)
- [Ручные источники: банки, карты, наличные, долги](docs_project/MANUAL_SOURCES.md)
- [Read-only API-ключи бирж](docs_project/EXCHANGE_KEYS.md)

## Архитектура

```
app/
  main.py            FastAPI (health, sources, plaid, exchanges, wallets,
                     portfolio, reports, recommendations, tradingview, market)
  config.py          настройки из .env
  database.py        SQLAlchemy
  models/            connected_sources, plaid_items, financial_accounts,
                     cash_entries, exchange_connections, crypto_holdings,
                     wallets, market_prices, watchlist_assets,
                     investment_recommendations, upcoming_obligations,
                     daily_snapshots, audit_log
  security/          encryption, api_key_validator, permissions,
                     guardrails, audit_log
  adapters/          ExchangeAdapter + CoinbaseAdapter + BybitAdapter
  services/          cfo_service (формулы), market_service (CMC/CoinGecko),
                     news_service (заготовка), plaid_service
  agents/            CFO, Accountant, Crypto, Market, News, Risk,
                     Discipline, Orchestrator
  reports/           ежедневный текст + PDF (reportlab) + PNG (Pillow)
  telegram/          бот (long polling) + отправка сообщений/файлов
  scheduler.py       утренний/вечерний отчёт по расписанию
tests/               guardrails, security, формулы CFO, API smoke
```

## Формулы

```
Freedom Ratio       = Monthly Passive Income / Monthly Expenses
Survival Ratio      = Liquid Cash / Monthly Expenses
Net Worth           = Total Assets - Total Liabilities
Today Free Cash     = Available Cash - Upcoming 14d Obligations - Emergency Buffer
Investment Capacity = Today Free Cash - Personal Spending Allowance
```

Freedom Ratio >= 1 — цель 2030 достигнута: пассивный доход покрывает расходы.

## TradingView webhook

`POST /webhooks/tradingview`

```json
{
  "symbol": "SOLUSDT",
  "signal": "BUY",
  "price": 120,
  "timeframe": "4H",
  "strategy": "trend_following",
  "confidence": "medium"
}
```

Сигнал сохраняется, сопоставляется с портфелем, проходит риск-проверку и
уходит alert'ом в Telegram. Автоматическая покупка невозможна по построению.

## Тесты

```bash
python -m pytest tests/ -q
```

Покрыто: все 8 правил guardrails, отклонение seed phrase / private key,
отклонение trade/withdraw ключей, шифрование секретов, формулы CFO,
smoke-тесты API (включая «секреты никогда не возвращаются»).
