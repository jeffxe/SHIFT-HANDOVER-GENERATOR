from agents import agent5_health

def test_health_score_empty():
    data = {
        "unique_incidents": []
    }
    result = agent5_health.run(data)
    assert result["health_score"] == 100
    assert result["health_grade"] == "A"
    assert result["health_breakdown"] == {}

def test_health_score_perfect():
    data = {
        "unique_incidents": [
            {"status": "resolved", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "resolved", "priority": "Low", "sla_risk": "Low Risk", "escalation_likely": False}
        ]
    }
    result = agent5_health.run(data)
    assert result["health_score"] == 100
    assert result["health_grade"] == "A"
    assert result["health_breakdown"]["resolution_rate"] == "100%"

def test_health_score_all_mitigated():
    data = {
        "unique_incidents": [
            {"status": "mitigated", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False}
        ]
    }
    result = agent5_health.run(data)
    # resolution_rate = (0 + 1 * 0.8) / 1 = 0.8
    # deduction_resolution = (1 - 0.8) * 30 = 6
    # penalty_priority = 0, penalty_sla = 0, penalty_esc = 0
    # raw = 100 - 6 = 94
    assert result["health_score"] == 94
    assert result["health_grade"] == "A"
    assert result["health_breakdown"]["resolution_rate"] == "80%"

def test_health_score_complex_deductions():
    data = {
        "unique_incidents": [
            {"status": "resolved", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "resolved", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "resolved", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "resolved", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "mitigated", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "mitigated", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            # 4 open
            {"status": "open", "priority": "Critical", "sla_risk": "High Risk", "escalation_likely": True},
            {"status": "open", "priority": "High", "sla_risk": "High Risk", "escalation_likely": True},
            {"status": "open", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False},
            {"status": "open", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False}
        ]
    }
    result = agent5_health.run(data)
    # Expected calculations:
    # total = 10
    # resolved = 4, mitigated = 2
    # resolution_rate = (4 + 1.6) / 10 = 0.56
    # deduction_resolution = (1.0 - 0.56) * 30 = 13.2
    # penalty_priority = min(1*15 + 1*8, 40) = 23
    # penalty_sla = min(2*5, 15) = 10
    # penalty_esc = min(2*5, 15) = 10
    # raw = 100 - 13.2 - 23 - 10 - 10 = 43.8
    # score = round(43.8) = 44
    assert result["health_score"] == 44
    assert result["health_grade"] == "D"
    assert result["health_breakdown"]["critical_open"] == 1
    assert result["health_breakdown"]["high_open"] == 1
    assert result["health_breakdown"]["sla_high_risk"] == 2
    assert result["health_breakdown"]["escalations"] == 2
    assert result["health_breakdown"]["deduction_resolution"] == 13.2
    assert result["health_breakdown"]["penalty_priority"] == 23
    assert result["health_breakdown"]["penalty_sla"] == 10
    assert result["health_breakdown"]["penalty_escalation"] == 10

def test_health_score_grades():
    # Boundary testing: A (>=85), B (70-84), C (55-69), D (40-54), F (<40)
    
    # Check grade B boundary (e.g. 70)
    # Total = 10, resolved = 0, mitigated = 0
    # resolution_rate = 0, deduction_resolution = 30
    # score = 70, grade = B
    data_b = {
        "unique_incidents": [{"status": "open", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False}] * 10
    }
    assert agent5_health.run(data_b)["health_grade"] == "B"
    assert agent5_health.run(data_b)["health_score"] == 70

    # Check grade C boundary (e.g. 55)
    # Total = 10, resolved = 0, mitigated = 0, deduction = 30
    # open critical = 1 -> penalty_priority = 15
    # score = 100 - 30 - 15 = 55, grade = C
    data_c = {
        "unique_incidents": (
            [{"status": "open", "priority": "Critical", "sla_risk": "Low Risk", "escalation_likely": False}] +
            [{"status": "open", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False}] * 9
        )
    }
    assert agent5_health.run(data_c)["health_grade"] == "C"
    assert agent5_health.run(data_c)["health_score"] == 55

    # Check grade F boundary (e.g. 30)
    # Total = 10, resolved = 0, mitigated = 0, deduction = 30
    # open critical = 3 -> penalty_priority = 40 (maxed)
    # score = 100 - 30 - 40 = 30, grade = F
    data_f = {
        "unique_incidents": (
            [{"status": "open", "priority": "Critical", "sla_risk": "Low Risk", "escalation_likely": False}] * 3 +
            [{"status": "open", "priority": "Medium", "sla_risk": "Low Risk", "escalation_likely": False}] * 7
        )
    }
    assert agent5_health.run(data_f)["health_grade"] == "F"
    assert agent5_health.run(data_f)["health_score"] == 30
