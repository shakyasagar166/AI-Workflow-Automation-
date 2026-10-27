import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
HEADERS = {settings.API_KEY_HEADER_NAME: settings.DEFAULT_API_KEY}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_get_dashboard_stats():
    response = client.get("/api/v1/stats", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "total_workflows" in data
    assert "total_executions" in data

def test_create_and_get_workflow():
    payload = {
        "name": "Integration Test Pipeline",
        "description": "Pipeline created during automated tests",
        "status": "active",
        "trigger_type": "manual",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "Start", "config": {}, "position": {"x": 0, "y": 0}},
            {"id": "n2", "type": "agent_planner", "name": "Plan", "config": {"goal": "Test plan"}, "position": {"x": 200, "y": 0}}
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"}
        ]
    }
    create_res = client.post("/api/v1/workflows", json=payload, headers=HEADERS)
    assert create_res.status_code == 201
    created_wf = create_res.json()
    wf_id = created_wf["id"]
    assert created_wf["name"] == payload["name"]

    # Fetch workflow by id
    get_res = client.get(f"/api/v1/workflows/{wf_id}", headers=HEADERS)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == wf_id

    # Clean up
    del_res = client.delete(f"/api/v1/workflows/{wf_id}", headers=HEADERS)
    assert del_res.status_code == 204

def test_cycle_detection_rejection():
    # Cyclical workflow n1 -> n2 -> n1
    payload = {
        "name": "Invalid Cyclical Pipeline",
        "description": "Should fail validation",
        "nodes": [
            {"id": "n1", "type": "trigger", "name": "N1"},
            {"id": "n2", "type": "agent_planner", "name": "N2"}
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n1"}
        ]
    }
    res = client.post("/api/v1/workflows", json=payload, headers=HEADERS)
    assert res.status_code == 400
    assert "cycle" in res.json()["detail"].lower()
