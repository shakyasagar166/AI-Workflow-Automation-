import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
HEADERS = {settings.API_KEY_HEADER_NAME: settings.DEFAULT_API_KEY}

def test_email_integration_endpoint():
    payload = {
        "to_email": "ops@enterprise.internal",
        "subject": "System Verification Alert",
        "body": "All workflow units operating nominally."
    }
    response = client.post("/api/v1/integrations/test-email", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ops@enterprise.internal" in data["message"]

    # Check outbox inspection endpoint
    outbox_res = client.get("/api/v1/integrations/email-outbox", headers=HEADERS)
    assert outbox_res.status_code == 200
    outbox = outbox_res.json()["outbox"]
    assert len(outbox) > 0

def test_webhook_integration_endpoint():
    payload = {
        "url": "https://api.example.com/test-webhook",
        "method": "POST",
        "payload": {"event": "test_ping", "status": "active"}
    }
    response = client.post("/api/v1/integrations/test-webhook", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status_code"] == 200

def test_llm_integration_endpoint():
    payload = {
        "prompt": "Evaluate and verify compliance of customer support response.",
        "provider": "mock",
        "system_instruction": "You are a quality assurance auditor."
    }
    response = client.post("/api/v1/integrations/test-llm", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "content" in data
