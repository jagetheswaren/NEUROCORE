import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from server.app import app
from server.api.dependencies import get_orchestrator, get_model_router, get_audit_logger

@pytest.fixture
def mock_orchestrator():
    orch = MagicMock()
    orch.model = MagicMock()
    orch.model.health_check.return_value = True
    orch.model.model = "qwen3:8b"
    orch.model.base_url = "http://127.0.0.1:11434"
    orch.history = []
    orch.run.return_value = "Mocked AI Response from Core"

    orch.permissions = MagicMock()
    orch.permissions.status.side_effect = lambda cmd: "auto" if "ls" in cmd else ("sensitive" if "rm" in cmd else ("blocked" if "shutdown" in cmd else "ask"))
    orch.execute_command.return_value = (True, "Command output")

    orch.memory_db = MagicMock()
    orch.memory_db.get_all.return_value = [(1, "Memory 1", "general", "2026-08-17")]
    orch.remember.return_value = "Memory saved successfully."
    orch.retrieve_memories.return_value = ["Memory 1"]
    
    orch.tts = None
    orch.speech = None
    return orch

@pytest.fixture
def mock_model_router():
    router = MagicMock()
    router.route.return_value = {
        "tier": "fast",
        "model": "qwen3:8b",
        "thinking": False,
        "temperature": 0.7,
        "max_tokens": 400
    }
    return router

@pytest.fixture
def client(mock_orchestrator, mock_model_router):
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[get_model_router] = lambda: mock_model_router
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["version"] == "0.5.0"

def test_chat_endpoint_success(client):
    payload = {"message": "Explain Python", "mode": "friend"}
    res = client.post("/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["response"] == "Mocked AI Response from Core"
    assert data["mode"] == "friend"

def test_chat_endpoint_empty_message(client):
    payload = {"message": "   ", "mode": "friend"}
    res = client.post("/chat", json=payload)
    assert res.status_code == 400

def test_memory_endpoints(client):
    res_list = client.get("/memory")
    assert res_list.status_code == 200
    assert res_list.json()["count"] == 1

    res_add = client.post("/memory", json={"content": "New user memory"})
    assert res_add.status_code == 200
    assert res_add.json()["status"] == "success"

def test_modes_endpoint(client):
    res = client.get("/modes")
    assert res.status_code == 200
    modes = res.json()["modes"]
    assert len(modes) >= 5

def test_tool_execution_auto_approve(client):
    res = client.post("/tool/execute", json={"command": "ls workspace/", "auto_approve_if_ask": True})
    assert res.status_code == 200
    assert res.json()["status"] == "executed"

def test_tool_execution_blocked(client):
    res = client.post("/tool/execute", json={"command": "shutdown -h now"})
    assert res.status_code == 403
