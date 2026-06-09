"""
Agent 6: Report Generation Agent
Uses Gemini to synthesise all agent outputs into a
structured Shift Handover Report in Markdown format.
"""

import json
from utils.ollama_client import call_ollama


REPORT_PROMPT = """
You are a senior support operations manager writing a shift handover report.
Use the structured SRE data below to produce a clear, professional operations handover note.

Format the report EXACTLY as follows (use Markdown):
- Do NOT output any introductory or concluding sentences (e.g., "Here is the report..."). Start directly with the H1 header "# Shift Handover Report".
- Use Markdown tables for the issues, risk alerts, and completed tasks sections.

---
# Shift Handover Report
**Shift Health Score:** {score}/100 (Grade: {grade})

## High Priority Issues
Render open Critical and High priority issues as a Markdown table.
Columns: Severity | Incident (ID & Title) | Owner | Status | Context (One-line reason)

## Risk Alerts
Render incidents flagged as High Risk or escalation likely as a Markdown table.
Columns: Incident (ID & Title) | SLA Risk | Escalation Likely | Risk Reason

## Completed Tasks
Render resolved incidents as a Markdown table.
Columns: Incident (ID & Title) | Owner | Resolution Summary

## Watchlist
Render open Medium and Low priority issues as a list. For each, show: `ID - Title (Owner)`

## Recommended Actions
Provide a bulleted list of 4–6 specific, actionable, professional recommendations for the incoming shift based on the data.

## Shift Summary
Brief 3–4 sentence business narrative summarizing the overall shift health and major events.
---

DATA:
{data_summary}
"""


def run(data: dict) -> dict:
    """
    Generates the final Shift Handover Report using Gemini.
    Adds 'report_markdown' to data.
    """
    score = data.get("health_score", 0)
    grade = data.get("health_grade", "?")

    # Build a concise data summary for the prompt
    incidents = data.get("unique_incidents", [])
    breakdown = data.get("health_breakdown", {})
    risk_alerts = data.get("risk_alerts", [])
    duplicates  = data.get("duplicates", [])

    data_summary = {
        "health_score":    score,
        "health_grade":    grade,
        "breakdown":       breakdown,
        "incidents": [
            {
                "id":               i["id"],
                "title":            i["title"],
                "status":           i.get("status", "Open"),
                "priority":         i.get("priority", "Medium"),
                "agent":            i.get("agent", ""),
                "sla_risk":         i.get("sla_risk", "Low Risk"),
                "escalation":       i.get("escalation_likely", False),
                "priority_reason":  i.get("priority_reason", ""),
                "risk_reason":      i.get("risk_reason", ""),
            }
            for i in incidents
        ],
        "duplicates_removed": len(duplicates),
        "total_raw":          data.get("total_raw", 0),
    }

    prompt = REPORT_PROMPT.format(
        score=score,
        grade=grade,
        data_summary=json.dumps(data_summary, indent=2),
    )

    report_markdown = call_ollama(prompt)

    data["report_markdown"] = report_markdown
    return data
