import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.entrypoints.api.main import app

@pytest.fixture
def workflow_payload():
    return {
        "name": "API Test Workflow",
        "version": "1.0.0",
        "initial_state": "IDLE",
        "states": {
            "IDLE": {
                "name": "IDLE",
                "next_state": "CODING"
            },
            "CODING": {
                "name": "CODING",
                "worker_type": "python_agent",
                "script": "agents/coder.py",
                "next_state": "TESTING",
                "on_failure": "FAILED"
            },
            "TESTING": {
                "name": "TESTING",
                "worker_type": "pytest_runner",
                "script": "agents/tester.py",
                "next_state": "AWAITING_APPROVAL",
                "on_failure": "CODING"
            },
            "AWAITING_APPROVAL": {
                "name": "AWAITING_APPROVAL",
                "require_human": True,
                "on_approve": "COMPLETED",
                "on_reject": "CODING"
            },
            "COMPLETED": {
                "name": "COMPLETED",
                "is_final": True
            },
            "FAILED": {
                "name": "FAILED",
                "is_final": True
            }
        }
    }

def test_api_workflow_lifecycle(workflow_payload):
    # Use TestClient context manager to trigger lifespan and database initialization
    with TestClient(app) as client:
        # 1. Create Workflow
        response = client.post("/api/workflows", json=workflow_payload)
        assert response.status_code == 200
        workflow_data = response.json()
        workflow_id = workflow_data["id"]
        assert workflow_data["name"] == "API Test Workflow"
        
        # 2. Create Instance
        instance_payload = {
            "workflow_id": workflow_id,
            "variables": {"project": "FlowForge REST API"}
        }
        response = client.post("/api/instances", json=instance_payload)
        assert response.status_code == 200
        instance_data = response.json()
        instance_id = instance_data["id"]
        assert instance_data["current_state"] == "IDLE"
        assert instance_data["variables"]["project"] == "FlowForge REST API"

        # 3. Connect to WebSocket and trigger transition to verify push update
        with client.websocket_connect(f"/ws/instances/{instance_id}") as websocket:
            # Trigger valid transition (START)
            transition_payload = {"event": "START", "triggered_by": "SYSTEM"}
            response = client.post(f"/api/instances/{instance_id}/transition", json=transition_payload)
            assert response.status_code == 200
            event_data = response.json()
            assert event_data["event_type"] == "STATE_CHANGED"
            
            # Verify websocket broadcast message received
            ws_msg = websocket.receive_json()
            assert ws_msg["event_type"] == "STATE_TRANSITION"
            assert ws_msg["from_state"] == "IDLE"
            assert ws_msg["to_state"] == "CODING"
            assert ws_msg["trigger_event"] == "START"

        # 4. Trigger invalid transition and verify HTTP 400 Bad Request
        # Cannot trigger APPROVE while in CODING state
        transition_payload = {"event": "APPROVE", "triggered_by": "USER_123"}
        response = client.post(f"/api/instances/{instance_id}/transition", json=transition_payload)
        assert response.status_code == 400
        assert "is invalid" in response.json()["detail"]

        # 5. Verify audit events log
        response = client.get(f"/api/instances/{instance_id}/events")
        assert response.status_code == 200
        events_log = response.json()
        assert len(events_log) == 1
        assert events_log[0]["event_type"] == "STATE_CHANGED"
