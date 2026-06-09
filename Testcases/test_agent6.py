from unittest.mock import patch
from agents import agent6_report

@patch("agents.agent6_report.call_ollama")
def test_run_report_generation(mock_call):
    mock_report = "# Shift Handover Report\n**Shift Health Score:** 80/100 (Grade: B)\n..."
    mock_call.return_value = mock_report

    data = {
        "health_score": 80,
        "health_grade": "B",
        "health_breakdown": {
            "total_incidents": 2,
            "resolved": 1,
            "mitigated": 0,
            "open": 1
        },
        "unique_incidents": [
            {
                "id": "T1",
                "title": "Incident 1",
                "status": "Open",
                "priority": "High",
                "agent": "alice",
                "sla_risk": "High Risk",
                "escalation_likely": True,
                "priority_reason": "Major bug",
                "risk_reason": "SLA breaches soon"
            }
        ],
        "duplicates": [],
        "total_raw": 1
    }

    result = agent6_report.run(data)

    # Verify that call_ollama was called
    mock_call.assert_called_once()
    
    # Check that report_markdown was attached correctly
    assert result["report_markdown"] == mock_report

    # Verify that the call argument contains expected text
    call_args, _ = mock_call.call_args
    prompt_sent = call_args[0]
    assert "80" in prompt_sent
    assert "T1" in prompt_sent
    assert "alice" in prompt_sent
