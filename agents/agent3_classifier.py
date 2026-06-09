"""
Agent 3: Priority Classification Agent
Uses Gemini to classify each unique incident as:
Critical / High / Medium / Low
"""

import json
from utils.ollama_client import call_ollama


PRIORITY_PROMPT = """
You are a senior support operations and support triage expert.
For each of the incidents listed below, determine both the support priority and the SLA risk parameters.

Priority levels:
- Critical: System down, revenue impact, data loss, security breach
- High: Major feature broken, SLA at risk, many users affected
- Medium: Partial degradation, workaround available, moderate impact
- Low: Minor issue, cosmetic, single user, enhancement request

SLA Risk levels:
- "High Risk", "Medium Risk", or "Low Risk" (depending on severity, impact, or hours remaining)
- Predict if escalation is likely: true or false
- Determine risk reason: a one-sentence explanation of the SLA risk

Return ONLY a valid JSON array. Each element in the array MUST contain exactly these keys:
  "id", "priority", "reason", "sla_risk", "escalation_likely", "risk_reason"

Incidents:
{incidents}
"""


def run(data: dict) -> dict:
    """
    Classifies each unique incident's priority and risk parameters using Ollama in a combined step.
    Adds 'priority', 'priority_reason', 'sla_risk', 'escalation_likely', and 'risk_reason' to each incident.
    """
    incidents = data["unique_incidents"]

    # Build a compact list for the prompt
    compact = [
        {
            "id":          inc["id"],
            "title":       inc["title"],
            "description": inc["description"][:200],
            "sla_hours":   inc.get("sla_hours"),
            "created_at":  inc.get("created_at", ""),
        }
        for inc in incidents
    ]

    prompt = PRIORITY_PROMPT.format(incidents=json.dumps(compact, indent=2))
    response_text = call_ollama(prompt, format="json", num_predict=2048)

    # Parse JSON response
    classified = _parse_json_response(response_text)
    priority_map = {item["id"]: item for item in classified}

    # Attach priority & risk info to each incident
    for inc in incidents:
        info = priority_map.get(inc["id"], {})
        inc["priority"]          = info.get("priority", "Medium")
        inc["priority_reason"]   = info.get("reason", "Classified by default.")
        inc["sla_risk"]          = info.get("sla_risk", "Low Risk")
        inc["escalation_likely"] = info.get("escalation_likely", False)
        inc["risk_reason"]       = info.get("risk_reason", "")

    # Sort: Critical → High → Medium → Low
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    incidents.sort(key=lambda x: order.get(x["priority"], 4))

    data["unique_incidents"] = incidents
    data["priority_summary"] = _summarise(incidents)

    return data


def _parse_json_response(text: str) -> list:
    """Safely extracts a JSON array from Gemini's response."""
    try:
        start = text.find("[")
        end   = text.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return []


def _summarise(incidents: list) -> dict:
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for inc in incidents:
        p = inc.get("priority", "Medium")
        counts[p] = counts.get(p, 0) + 1
    return counts
