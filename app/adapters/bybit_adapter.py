"""Bybit read-only adapter (v5 API).

Signs wallet-balance and key-info requests when credentials are present;
otherwise returns an empty snapshot. No trade/withdraw endpoints here.
"""

import hashlib
import hmac
import time

import httpx

from app.adapters.base import ExchangeAdapter, ExchangeBalance, register_adapter

API_BASE = "https://api.bybit.com"
RECV_WINDOW = "5000"


@register_adapter
class BybitAdapter(ExchangeAdapter):
    exchange_name = "bybit"

    def _signed_headers(self, query: str = "") -> dict:
        timestamp = str(int(time.time() * 1000))
        payload = timestamp + self.api_key + RECV_WINDOW + query
        signature = hmac.new(
            self.api_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        return {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": RECV_WINDOW,
            "X-BAPI-SIGN": signature,
        }

    def detect_permissions(self) -> list[str]:
        if not self.api_key:
            return []
        try:
            resp = httpx.get(
                f"{API_BASE}/v5/user/query-api",
                headers=self._signed_headers(),
                timeout=10,
            )
            resp.raise_for_status()
            result = resp.json().get("result", {})
            labels = ["read"] if result.get("readOnly") in (1, True) else []
            perms = result.get("permissions", {}) or {}
            for group, entries in perms.items():
                lowered = group.lower()
                if entries and ("trade" in lowered or "options" in lowered or "spot" in lowered):
                    labels.append("trade")
                if entries and ("withdraw" in lowered or "wallet" in lowered):
                    labels.append("withdraw")
            return labels or ["unknown"]
        except Exception:
            return ["unknown"]

    def fetch_balances(self) -> list[ExchangeBalance]:
        if not self.api_key:
            return []
        query = "accountType=UNIFIED"
        resp = httpx.get(
            f"{API_BASE}/v5/account/wallet-balance?{query}",
            headers=self._signed_headers(query),
            timeout=15,
        )
        resp.raise_for_status()
        balances = []
        for account in resp.json().get("result", {}).get("list", []):
            for coin in account.get("coin", []):
                amount = float(coin.get("walletBalance", 0) or 0)
                if amount <= 0:
                    continue
                usd = float(coin.get("usdValue", 0) or 0) or None
                balances.append(
                    ExchangeBalance(symbol=coin.get("coin", "?"), amount=amount, usd_value=usd)
                )
        return balances
