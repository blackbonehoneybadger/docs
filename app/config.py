"""Application settings loaded from environment / .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Core
    database_url: str = "sqlite:///./badger_cfo.db"
    telegram_bot_token: str = ""

    # PWA / web app access code. When set, the web app and API require it.
    # Leave empty ONLY for local development. MUST be set for any public deploy.
    app_access_code: str = ""

    # Encryption key for secrets at rest (Fernet). Generate with:
    #   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    fernet_key: str = ""

    # Plaid (read-only products only — transfer/payment products are forbidden)
    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"
    plaid_products: str = "transactions,balance,liabilities,investments"
    plaid_country_codes: str = "US"

    # Market data
    coinmarketcap_api_key: str = ""
    coingecko_api_key: str = ""

    # Exchanges (read-only API keys only)
    coinbase_api_key: str = ""
    coinbase_api_secret: str = ""
    bybit_api_key: str = ""
    bybit_api_secret: str = ""
    binance_api_key: str = ""
    binance_api_secret: str = ""

    robinhood_mode: str = "manual"

    news_api_key: str = ""

    # Reports
    report_timezone: str = "America/New_York"
    morning_report_time: str = "08:00"
    evening_report_time: str = "21:00"

    # Financial policy knobs
    emergency_buffer: float = 200.0
    obligation_horizon_days: int = 14
    personal_spending_ratio: float = 0.3  # share of free cash allowed for personal spending


@lru_cache
def get_settings() -> Settings:
    return Settings()
