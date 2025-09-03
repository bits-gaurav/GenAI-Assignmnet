import pytest
import sys
import os
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_home_route():
    """Test home route returns running message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Pipeline Monitor Running" in response.json()["message"]

@pytest.mark.asyncio
async def test_webhook_failure_triggers_alert_and_rollback(monkeypatch):
    """Simulate workflow failure and check Slack + rollback triggers"""
    triggered = {"slack": False, "rollback": False}

    async def fake_send_slack_alert(message: str):
        triggered["slack"] = True

    async def fake_trigger_rollback(repo: str):
        triggered["rollback"] = True

    # Import the module to patch it
    from app import main
    monkeypatch.setattr(main, "send_slack_alert", fake_send_slack_alert)
    monkeypatch.setattr(main, "trigger_rollback", fake_trigger_rollback)

    payload = {
        "workflow_run": {"conclusion": "failure"},
        "repository": {"full_name": "test/repo"},
        "sender": {"login": "tester"}
    }

    response = client.post("/github-webhook", json=payload)
    assert response.status_code == 200
    assert triggered["slack"] is True
    assert triggered["rollback"] is True

@pytest.mark.asyncio
async def test_webhook_success_does_not_trigger(monkeypatch):
    """Simulate workflow success and ensure no Slack/rollback"""
    triggered = {"slack": False, "rollback": False}

    async def fake_send_slack_alert(message: str):
        triggered["slack"] = True

    async def fake_trigger_rollback(repo: str):
        triggered["rollback"] = True

    # Import the module to patch it
    from app import main
    monkeypatch.setattr(main, "send_slack_alert", fake_send_slack_alert)
    monkeypatch.setattr(main, "trigger_rollback", fake_trigger_rollback)

    payload = {
        "workflow_run": {"conclusion": "success"},
        "repository": {"full_name": "test/repo"},
        "sender": {"login": "tester"}
    }

    response = client.post("/github-webhook", json=payload)
    assert response.status_code == 200
    assert triggered["slack"] is False
    assert triggered["rollback"] is False
