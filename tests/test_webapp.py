"""PWA shell + /api + access-code gate."""

import importlib

from fastapi.testclient import TestClient

import app.config as config
from app.main import app

client = TestClient(app)


def test_pwa_shell_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Badger CFO" in resp.text


def test_manifest_and_sw():
    m = client.get("/manifest.webmanifest")
    assert m.status_code == 200
    assert "standalone" in m.text
    sw = client.get("/sw.js")
    assert sw.status_code == 200
    assert "badger-cfo" in sw.text


def test_icons_present():
    assert client.get("/static/icons/icon-192.png").status_code == 200
    assert client.get("/static/icons/icon-512.png").status_code == 200


def test_api_summary_open_mode():
    # No access code configured in tests -> API is open.
    resp = client.get("/api/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert "net_worth" in body and "freedom_ratio" in body


def test_api_cash_and_summary_flow():
    assert client.post("/api/cash", json={"amount": 500, "type": "cash_income"}).status_code == 200
    assert client.get("/api/summary").json()["total_cash"] >= 500


def test_auth_status_open():
    assert client.get("/auth/status").json()["access_required"] is False


def test_access_code_gate(monkeypatch):
    # Turn on an access code and verify the gate engages.
    config.get_settings.cache_clear()
    monkeypatch.setenv("APP_ACCESS_CODE", "1234")
    config.get_settings.cache_clear()
    try:
        gated = TestClient(app)
        assert gated.get("/auth/status").json()["access_required"] is True
        # Without code -> 401
        assert gated.get("/api/summary").status_code == 401
        # Wrong code -> 401
        assert gated.post("/auth/login", json={"code": "0000"}).status_code == 401
        # Right code -> cookie set, then access works
        ok = gated.post("/auth/login", json={"code": "1234"})
        assert ok.status_code == 200
        assert gated.get("/api/summary").status_code == 200
        # Header form also works on a fresh client
        fresh = TestClient(app)
        assert fresh.get("/api/summary", headers={"X-Access-Code": "1234"}).status_code == 200
    finally:
        monkeypatch.delenv("APP_ACCESS_CODE", raising=False)
        config.get_settings.cache_clear()
