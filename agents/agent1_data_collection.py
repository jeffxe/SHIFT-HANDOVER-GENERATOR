"""
Agent 1: Data Collection Agent
Reads and parses JSON chat logs and CSV ticket data,
then merges them into a unified list of incidents.
"""

import json
import pandas as pd
from datetime import datetime


def run(chat_file, ticket_file) -> dict:
    """
    Reads uploaded chat logs (JSON) and ticket data (CSV).
    Returns a unified dict with parsed chats and tickets.
    """
    # --- Parse chat logs ---
    chat_content = chat_file.read()
    if isinstance(chat_content, bytes):
        chat_content = chat_content.decode("utf-8")
    chats = json.loads(chat_content)

    # Normalise chat entries
    chat_incidents = []
    for c in chats:
        chat_incidents.append({
            "source":      "chat",
            "id":          c.get("id", ""),
            "title":       c.get("message", "")[:80],
            "description": c.get("message", ""),
            "agent":       c.get("agent", "Unknown"),
            "status":      "Open",
            "category":    ", ".join(c.get("tags", [])),
            "created_at":  c.get("timestamp", ""),
            "sla_hours":   None,
        })

    # --- Parse ticket CSV ---
    ticket_file.seek(0)
    df = pd.read_csv(ticket_file)
    df.columns = [col.strip().lower() for col in df.columns]

    ticket_incidents = []
    for _, row in df.iterrows():
        ticket_incidents.append({
            "source":      "ticket",
            "id":          str(row.get("ticket_id", "")),
            "title":       str(row.get("title", "")),
            "description": str(row.get("description", "")),
            "agent":       str(row.get("assigned_to", "Unassigned")),
            "status":      str(row.get("status", "Open")),
            "category":    str(row.get("category", "")),
            "created_at":  str(row.get("created_at", "")),
            "sla_hours":   row.get("sla_hours", None),
        })

    all_incidents = chat_incidents + ticket_incidents

    return {
        "chats":        chats,
        "tickets":      df.to_dict(orient="records"),
        "all_incidents": all_incidents,
        "total_raw":    len(all_incidents),
    }
