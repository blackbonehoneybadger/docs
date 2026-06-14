# Ручные источники: банки, карты, наличные, долги, обязательства

Всё, что нельзя подключить автоматически, вносится вручную — через
Telegram или REST API.

## Через Telegram

```
/add_cash_income 300 работа        — наличный доход
/add_cash_expense 50 еда           — наличный расход
/add_card CreditOne 300 120        — кредитка: имя, лимит, баланс
/add_card Discover 1000 400
/add_exchange Bybit                — биржа как manual source
/add_wallet Cold1 Solana <адрес>   — холодный кошелёк (ПУБЛИЧНЫЙ адрес)
```

Важно: если отправишь боту seed phrase или private key — он откажется
сохранять и предупредит. Так задумано.

## Через API

Карта/банк/долг:

```bash
curl -X POST http://localhost:8000/accounts/manual -H "Content-Type: application/json" -d '{
  "name": "Credit One",
  "account_type": "credit_card",
  "current_balance": 120,
  "credit_limit": 300,
  "minimum_payment": 30,
  "next_due_date": "2026-06-25"
}'
```

`account_type`: `checking`, `savings`, `credit_card`, `loan`, `investment`,
`cash`, `business`, `other`.

Обязательный платёж (lease, страховка, телефон, подписки):

```bash
curl -X POST http://localhost:8000/obligations -H "Content-Type: application/json" -d '{
  "name": "Car lease",
  "amount": 399,
  "due_date": "2026-06-20",
  "frequency": "monthly"
}'
```

Крипто-позиция вручную (вне биржи или без API-ключа):

```bash
curl -X POST http://localhost:8000/exchanges/holdings/manual -H "Content-Type: application/json" -d '{
  "symbol": "SOL",
  "amount": 10,
  "average_buy_price": 95,
  "location": "cold_wallet",
  "wallet_name": "Cold1"
}'
```

Цена вручную (если нет API-ключей маркет-данных):

```bash
curl -X POST http://localhost:8000/market/prices/manual -H "Content-Type: application/json" -d '{
  "symbol": "SOL", "price": 120, "change_24h": -3.2
}'
```

После любых изменений `/sync_all` в боте пересчитает стоимость позиций.
