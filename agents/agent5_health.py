"""
Agent 5: Health Score Agent
Calculates a 0–100 Shift Health Score based on:
  - Resolution rate
  - Open Critical/High count
  - SLA risk profile
  - Escalation count
"""


def run(data: dict) -> dict:
    """
    Computes Shift Health Score and a health grade (A–F).
    Adds 'health_score', 'health_grade', 'health_breakdown' to data.
    """
    incidents = data["unique_incidents"]
    total     = len(incidents)

    if total == 0:
        data["health_score"]     = 100
        data["health_grade"]     = "A"
        data["health_breakdown"] = {}
        return data

    # --- Component calculations ---
    resolved = [i for i in incidents if i.get("status", "").lower() == "resolved"]
    mitigated = [i for i in incidents if i.get("status", "").lower() == "mitigated"]
    open_inc = [i for i in incidents if i.get("status", "").lower() not in ("resolved", "mitigated")]

    # Mitigated incidents contribute 80% towards resolution rating
    resolution_rate = (len(resolved) + len(mitigated) * 0.8) / total  # 0.0 – 1.0
    deduction_resolution = (1.0 - resolution_rate) * 30

    # Penalty: −15 per Critical open, −8 per High open (max −40)
    open_critical = sum(1 for i in open_inc if i.get("priority") == "Critical")
    open_high     = sum(1 for i in open_inc if i.get("priority") == "High")
    penalty_priority = min((open_critical * 15) + (open_high * 8), 40)

    # Penalty: −5 per active SLA High Risk (max −15)
    active_high_risk_sla = sum(1 for i in open_inc if i.get("sla_risk") == "High Risk")
    penalty_sla = min(active_high_risk_sla * 5, 15)

    # Penalty: −5 per active escalation (max −15)
    active_escalations = sum(1 for i in open_inc if i.get("escalation_likely"))
    penalty_esc = min(active_escalations * 5, 15)

    # Base score starts at 100
    raw = 100 - deduction_resolution - penalty_priority - penalty_sla - penalty_esc
    score = max(0, min(100, round(raw)))

    # --- Grade ---
    if score >= 85:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 55:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    data["health_score"] = score
    data["health_grade"] = grade
    data["health_breakdown"] = {
        "total_incidents":   total,
        "resolved":          len(resolved),
        "mitigated":         len(mitigated),
        "open":              len(open_inc),
        "resolution_rate":   f"{resolution_rate * 100:.0f}%",
        "critical_open":     open_critical,
        "high_open":         open_high,
        "sla_high_risk":     active_high_risk_sla,
        "escalations":       active_escalations,
        "deduction_resolution": round(deduction_resolution, 1),
        "penalty_priority":  penalty_priority,
        "penalty_sla":       penalty_sla,
        "penalty_escalation":penalty_esc,
    }

    return data
