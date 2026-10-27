import pytest
from app.engine.dependency_resolver import DependencyResolver
from app.engine.retry_handler import RetryHandler
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)
HEADERS = {settings.API_KEY_HEADER_NAME: settings.DEFAULT_API_KEY}

def test_dependency_resolver_interpolation():
    context = {
        "trigger": {"user_id": "usr_99", "email": "test@domain.com"},
        "steps": {
            "step_1": {
                "output": {"score": 0.95, "sentiment": "positive"}
            }
        }
    }

    template_dict = {
        "to": "{{trigger.email}}",
        "result_score": "{{steps.step_1.output.score}}",
        "message": "User {{trigger.user_id}} has sentiment: {{steps.step_1.output.sentiment}}"
    }

    resolved = DependencyResolver.interpolate_value(template_dict, context)
    assert resolved["to"] == "test@domain.com"
    assert resolved["result_score"] == 0.95
    assert resolved["message"] == "User usr_99 has sentiment: positive"

def test_retry_handler_policy():
    handler = RetryHandler(max_retries=3)
    # Should retry under limit
    assert handler.should_retry(attempt=1, error=Exception("Transient network timeout")) is True
    assert handler.should_retry(attempt=2, output={"requires_retry": True}) is True
    # Should not retry once max_retries reached
    assert handler.should_retry(attempt=3, error=Exception("Timeout")) is False

def test_full_workflow_execution():
    # Create workflow
    payload = {
        "name": "End-to-End Test DAG",
        "description": "Trigger -> Planner -> Execution -> Verifier",
        "nodes": [
            {
                "id": "t1",
                "type": "trigger",
                "name": "Start Node",
                "config": {"default_payload": {"sample_key": "sample_value"}},
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "p1",
                "type": "agent_planner",
                "name": "Plan Node",
                "config": {"goal": "Test plan creation"},
                "position": {"x": 200, "y": 0}
            },
            {
                "id": "v1",
                "type": "agent_verifier",
                "name": "Verify Node",
                "config": {"candidate_output": "{{steps.p1.output.plan}}"},
                "position": {"x": 400, "y": 0}
            }
        ],
        "edges": [
            {"id": "e1", "source": "t1", "target": "p1"},
            {"id": "e2", "source": "p1", "target": "v1"}
        ]
    }
    wf_res = client.post("/api/v1/workflows", json=payload, headers=HEADERS)
    assert wf_res.status_code == 201
    wf_id = wf_res.json()["id"]

    # Execute workflow synchronously
    exec_res = client.post(
        f"/api/v1/workflows/{wf_id}/execute",
        json={"trigger_payload": {"user": "Alice"}, "run_async": False},
        headers=HEADERS
    )
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] == "COMPLETED"
    assert len(exec_data["step_executions"]) == 3
    assert exec_data["result"] is not None

    # Verify execution logs can be queried
    logs_res = client.get(f"/api/v1/executions/{exec_data['id']}/logs", headers=HEADERS)
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) > 0
