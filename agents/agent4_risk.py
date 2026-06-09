"""
Agent 4: Risk Prediction Agent
Analyses classified incidents and uses Gemini to predict
SLA risks and escalation likelihood for each open incident.
"""

import json
from utils.ollama_client import call_ollama


RISK_PROMPT = """
You are a senior support operations analyst. Analyse these open incidents and predict SLA risk.

For each incident, determine:
- sla_risk: "High Risk", "Medium Risk", or "Low Risk"
- escalation_likely: true or false
- risk_reason: one sentence explaining the risk

Return ONLY a valid JSON array. Each element must have:
  "id", "title", "sla_risk", "escalation_likely", "risk_reason"

Incidents:
{incidents}
"""


def run(data: dict) -> dict:
    """
    Extracts SLA risk and escalation flags that were already classified
    by the combined classifier step in Agent 3.
    """
    incidents = data["unique_incidents"]

    # Build risk alerts list (High Risk incidents or likely escalations)
    risk_alerts = [
        inc for inc in incidents
        if inc.get("sla_risk") == "High Risk" or inc.get("escalation_likely")
    ]

    data["unique_incidents"] = incidents
    data["risk_alerts"]      = risk_alerts

    return data
