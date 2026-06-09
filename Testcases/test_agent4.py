from agents import agent4_risk

def test_run_risk_filtering():
    data = {
        "unique_incidents": [
            {
                "id": "T1",
                "title": "Incident 1",
                "sla_risk": "High Risk",
                "escalation_likely": False
            },
            {
                "id": "T2",
                "title": "Incident 2",
                "sla_risk": "Low Risk",
                "escalation_likely": True
            },
            {
                "id": "T3",
                "title": "Incident 3",
                "sla_risk": "Medium Risk",
                "escalation_likely": False
            }
        ]
    }

    result = agent4_risk.run(data)

    # Assertions
    assert "risk_alerts" in result
    assert len(result["risk_alerts"]) == 2
    
    # Check that T1 and T2 are included in risk_alerts
    alert_ids = [alert["id"] for alert in result["risk_alerts"]]
    assert "T1" in alert_ids
    assert "T2" in alert_ids
    assert "T3" not in alert_ids
