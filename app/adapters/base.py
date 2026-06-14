"""ExchangeAdapter interface.

Every exchange (Coinbase, Binance, Bybit, Kraken, OKX, KuCoin, Crypto.com,
Bitget, MEXC, Gate.io, Robinhood, ...) implements this read-only contract.
Adapters must NEVER expose trade or withdrawal calls.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.security.api_key_validator import ValidationResult, validate_exchange_permissions


@dataclass
class ExchangeBalance:
    symbol: str
    amount: float
    usd_value: float | None = None
    staking: bool = False


class ExchangeAdapter(ABC):
    exchange_name: str = "abstract"

    def __init__(self, api_key: str = "", api_secret: str = "", passphrase: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase

    @abstractmethod
    def detect_permissions(self) -> list[str]:
        """Return permission labels reported by the exchange for this key."""

    @abstractmethod
    def fetch_balances(self) -> list[ExchangeBalance]:
        """Read-only balance snapshot."""

    def validate_read_only(self) -> ValidationResult:
        """Reject keys with trade/withdraw permission before saving them."""
        return validate_exchange_permissions(self.detect_permissions())


_REGISTRY: dict[str, type[ExchangeAdapter]] = {}


def register_adapter(cls: type[ExchangeAdapter]) -> type[ExchangeAdapter]:
    _REGISTRY[cls.exchange_name.lower()] = cls
    return cls


def get_adapter(exchange_name: str, **credentials) -> ExchangeAdapter:
    try:
        cls = _REGISTRY[exchange_name.lower()]
    except KeyError:
        supported = ", ".join(sorted(_REGISTRY)) or "none"
        raise ValueError(
            f"Биржа '{exchange_name}' пока не поддерживается. Доступны: {supported}. "
            "Добавь её вручную через /add_exchange как manual source."
        ) from None
    return cls(**credentials)
