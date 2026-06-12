"""API smoke tests through the FastAPI test client."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["read_only"] is True


def test_manual_flow_cash_card_obligation_portfolio():
    assert client.post("/cash", json={"amount": 300, "type": "cash_income",
                                      "description": "работа"}).status_code == 200
    assert client.post("/cash", json={"amount": 50, "type": "cash_expense",
                                      "description": "еда"}).status_code == 200
    assert client.post("/accounts/manual", json={
        "name": "Credit One", "account_type": "credit_card",
        "current_balance": 120, "credit_limit": 300,
    }).status_code == 200
    assert client.post("/obligations", json={
        "name": "Car lease", "amount": 399, "due_date": "2099-01-01",
    }).status_code == 200

    portfolio = client.get("/portfolio").json()
    assert portfolio["total_liabilities"] == 120.0

    risk = client.get("/portfolio/risk")
    assert risk.status_code == 200


def test_wallet_rejects_private_key():
    resp = client.post("/wallets", json={
        "wallet_name": "Bad", "chain": "Ethereum",
        "public_address": "0x" + "ab" * 32,
    })
    assert resp.status_code == 400
    assert "private key" in resp.json()["detail"].lower() or "приватн" in resp.json()["detail"].lower()


def test_wallet_accepts_public_address():
    resp = client.post("/wallets", json={
        "wallet_name": "Cold 1", "chain": "Solana",
        "public_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    })
    assert resp.status_code == 200


def test_tradingview_webhook_saves_and_never_trades():
    resp = client.post("/webhooks/tradingview", json={
        "symbol": "SOLUSDT", "signal": "BUY", "price": 120,
        "timeframe": "4H", "strategy": "trend_following", "confidence": "medium",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["auto_trade"] is False


def test_recommendations_require_approval():
    rows = client.get("/recommendations/today").json()
    for row in rows:
        assert row["requires_user_approval"] is True
        assert row["status"] == "proposed"


def test_reports_text_and_files():
    resp = client.get("/reports/morning")
    assert resp.status_code == 200
    assert "Boss My Life Report" in resp.text

    pdf = client.get("/reports/daily/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"

    img = client.get("/reports/daily/image")
    assert img.status_code == 200
    assert img.headers["content-type"] == "image/png"


def test_exchange_secrets_never_returned():
    client.post("/exchanges/add", json={"exchange_name": "bybit",
                                        "api_key": "", "api_secret": ""})
    rows = client.get("/exchanges").json()
    for row in rows:
        assert "api_key" not in row
        assert "encrypted_api_key" not in row
