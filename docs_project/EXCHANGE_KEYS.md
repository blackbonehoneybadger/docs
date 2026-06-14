# Read-only API-ключи бирж

## Правила

1. Создавай ключ ТОЛЬКО с правами чтения (read / read-only / view).
2. НИКОГДА не включай trade, withdraw, transfer.
3. Система проверяет права ключа при добавлении: ключи с trade/withdraw
   отклоняются, неизвестные права дают предупреждение.
4. Ключи хранятся зашифрованными (Fernet) и никогда не показываются
   в Telegram или ответах API.

## Как создать read-only ключ

**Bybit:** Profile → API → Create New Key → System-generated →
Read-Only → без галочек на Trade/Withdraw → привязка к IP желательна.

**Coinbase:** Settings → API → New API Key → только scope
`wallet:accounts:read` (и `wallet:user:read`). Никаких send/trade scope.

**Binance:** API Management → Create API → оставить только
"Enable Reading". Снять "Enable Spot & Margin Trading" и "Enable Withdrawals".

## Добавление в систему

```bash
curl -X POST http://localhost:8000/exchanges/add -H "Content-Type: application/json" -d '{
  "exchange_name": "bybit",
  "api_key": "...",
  "api_secret": "..."
}'
```

Ответ покажет `permissions_detected`. Если ключ имеет запрещённые права —
получишь 400 и ключ НЕ будет сохранён.

Синхронизация балансов:

```bash
curl -X POST http://localhost:8000/exchanges/sync
```

## Поддерживаемые адаптеры

Сейчас реализованы: **Coinbase**, **Bybit**.
Архитектура (`app/adapters/base.py`, интерфейс `ExchangeAdapter`) готова для
Binance, Kraken, OKX, KuCoin, Crypto.com, Bitget, MEXC, Gate.io, Robinhood —
новый адаптер это один класс с двумя методами (`detect_permissions`,
`fetch_balances`) и декоратором `@register_adapter`.

Биржи без адаптера добавляй как manual source: `/add_exchange Kraken` в боте,
а балансы — через `POST /exchanges/holdings/manual`.
