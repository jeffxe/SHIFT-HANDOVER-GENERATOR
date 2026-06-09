import json
from unittest.mock import patch
from agents import agent3_classifier

def test_parse_json_response_clean():
    text = '[{"id": "T1", "priority": "Critical"}]'
    result = agent3_classifier._parse_json_response(text)
    assert len(result) == 1
    assert result[0]["id"] == "T1"

def test_parse_json_response_with_markdown():
    text = 'Some prefix text\n```json\n[{"id": "T1", "priority": "Critical"}]\n```\nSome suffix'
    result = agent3_classifier._parse_json_response(text)
    assert len(result) == 1
    assert result[0]["id"] == "T1"

def test_parse_json_response_invalid():
    text = '[{"id": "T1", "priority": "Critical"' # missing brackets
    result = agent3_classifier._parse_json_response(text)
    assert result == []

def test_summarise():
    incidents = [
        {"priority": "Critical"},
        {"priority": "High"},
        {"priority": "High"},
        {"priority": "Low"},
        {"priority": "Medium"}
    ]
    summary = agent3_classifier._summarise(incidents)
    assert summary["Critical"] == 1
    assert summary["High"] == 2
    assert summary["Medium"] == 1
    assert summary["Low"] == 1

@patch("agents.agent3_classifier.call_ollama")
def test_run_happy_path(mock_call):
    # Setup mock response from Ollama
    mock_response = json.dumps([
        {
            "id": "CHAT-1",
            "priority": "Critical",
            "reason": "Database is down impacting transactions.",
            "sla_risk": "High Risk",
            "escalation_likely": True,
            "risk_reason": "SLA breaches in 1 hour."
        },
        {
            "id": "TKT-2",
            "priority": "Low",
            "reason": "Typo in standard documentation.",
            "sla_risk": "Low Risk",
            "escalation_likely": False,
            "risk_reason": "No SLA threat."
        }
    ])
    mock_call.return_value = mock_response

    # Input data
    data = {
        "unique_incidents": [
            {
                "id": "TKT-2",
                "title": "Documentation typo",
                "description": "Found a typo on page 5.",
                "source": "ticket"
            },
            {
                "id": "CHAT-1",
                "title": "Database down",
                "description": "Production database is totally down.",
                "source": "chat"
            }
        ]
    }

    result = agent3_classifier.run(data)

    # Check that call_ollama was invoked
    mock_call.assert_called_once()

    # Check sorting order: Critical should come first, then Low
    incidents = result["unique_incidents"]
    assert incidents[0]["id"] == "CHAT-1"
    assert incidents[0]["priority"] == "Critical"
    assert incidents[0]["priority_reason"] == "Database is down impacting transactions."
    assert incidents[0]["sla_risk"] == "High Risk"
    assert incidents[0]["escalation_likely"] is True
    assert incidents[0]["risk_reason"] == "SLA breaches in 1 hour."

    assert incidents[1]["id"] == "TKT-2"
    assert incidents[1]["priority"] == "Low"
    assert incidents[1]["priority_reason"] == "Typo in standard documentation."
    assert incidents[1]["sla_risk"] == "Low Risk"
    assert incidents[1]["escalation_likely"] is False
    assert incidents[1]["risk_reason"] == "No SLA threat."

    # Check summary counts
    assert result["priority_summary"]["Critical"] == 1
    assert result["priority_summary"]["Low"] == 1
    assert result["priority_summary"]["Medium"] == 0
    assert result["priority_summary"]["High"] == 0
