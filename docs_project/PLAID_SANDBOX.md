# Plaid Sandbox: подключение банков (read-only)

Plaid даёт доступ к балансам, транзакциям, liabilities и инвестициям.
Мы используем ТОЛЬКО read-only продукты. Продукты перевода денег
(`transfer`, `payment_initiation`) запрещены на уровне кода и будут
отклонены с ошибкой.

## 1. Регистрация

1. Зарегистрируйся на https://dashboard.plaid.com/signup (бесплатно).
2. В разделе **Team Settings → Keys** возьми `client_id` и `sandbox` secret.
3. Вставь их в `.env`:

   ```
   PLAID_CLIENT_ID=твой_client_id
   PLAID_SECRET=твой_sandbox_secret
   PLAID_ENV=sandbox
   ```

## 2. Подключение тестового банка

1. Запусти API: `uvicorn app.main:app`
2. Создай link token:

   ```bash
   curl -X POST http://localhost:8000/plaid/create_link_token
   ```

3. Используй `link_token` в [Plaid Link](https://plaid.com/docs/link/) —
   в sandbox-режиме логин `user_good`, пароль `pass_good`.
4. Link вернёт `public_token`. Обменяй его:

   ```bash
   curl -X POST http://localhost:8000/plaid/exchange_public_token \
     -H "Content-Type: application/json" \
     -d '{"public_token": "public-sandbox-..."}'
   ```

   Access token шифруется (Fernet) и сохраняется в `plaid_items`.

5. Синхронизируй счета:

   ```bash
   curl -X POST http://localhost:8000/plaid/sync
   curl http://localhost:8000/plaid/accounts
   ```

После синка балансы попадают в общий расчёт net worth и cashflow,
а кредитки — в долги и utilization.

## 3. Реальные банки

Когда будешь готов: смени `PLAID_ENV` на `development`/`production`
(нужен запрос production-доступа в Plaid Dashboard). Код не меняется.

Chase, Capital One, Discover доступны через Plaid. Credit One и PayPal —
проверь доступность в Plaid; если их нет, добавь их вручную
(см. MANUAL_SOURCES.md).
