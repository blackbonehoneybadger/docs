"""Coinbase read-only adapter.

Working skeleton: signs requests for the Coinbase Advanced/v2 accounts
endpoint when credentials are present; otherwise returns an empty snapshot so
manual flows keep working. No trade/withdraw endpoints exist in this class.
"""

import hashlib
import hmac
import time

import httpx

from app.adapters.base import ExchangeAdapter, ExchangeBalance, register_adapter

API_BASE = "https://api.coinbase.com"


@register_adapter
class CoinbaseAdapter(ExchangeAdapter):
    exchange_name = "coinbase"

    def _signed_headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time()))
        message = timestamp + method.upper() + path + body
        signature = hmac.new(
            self.api_secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp,
        }

    def detect_permissions(self) -> list[str]:
        if not self.api_key:
            return []
        try:
            path = "/v2/user/auth"
            resp = httpx.get(
                API_BASE + path, headers=self._signed_headers("GET", path), timeout=10
            )
            resp.raise_for_status()
            scopes = resp.json().get("data", {}).get("scopes", [])
            # wallet:accounts:read -> "read"; anything with trade/send -> forbidden labels
            labels = []
            for scope in scopes:
                if "send" in scope or "withdraw" in scope:
                    labels.append("withdraw")
                elif "trade" in scope or "buy" in scope or "sell" in scope:
                    labels.append("trade")
                else:
                    labels.append("read")
            return labels or ["read"]
        except Exception:
            # Cannot verify -> let the validator surface a warning, not a crash.
            return ["unknown"]

    def fetch_balances(self) -> list[ExchangeBalance]:
        if not self.api_key:
            return []
        path = "/v2/accounts"
        resp = httpx.get(
            API_BASE + path, headers=self._signed_headers("GET", path), timeout=15
        )
        resp.raise_for_status()
        balances = []
        for account in resp.json().get("data", []):
            amount = float(account.get("balance", {}).get("amount", 0) or 0)
            if amount <= 0:
                continue
            balances.append(
                ExchangeBalance(
                    symbol=account.get("balance", {}).get("currency", "?"),
                    amount=amount,
                )
            )
        return balances
