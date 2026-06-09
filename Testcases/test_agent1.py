import io
import json
import pandas as pd
from agents import agent1_data_collection

def test_agent1_data_collection_happy_path():
    # Sample chat data (JSON)
    chat_data = [
        {
            "id": "CHAT-1001",
            "message": "Database memory leak detected on production server.",
            "agent": "alice",
            "tags": ["database", "prod"],
            "timestamp": "2026-06-09T10:00:00Z"
        }
    ]
    chat_stream = io.StringIO(json.dumps(chat_data))

    # Sample ticket data (CSV)
    ticket_csv = (
        "ticket_id,title,description,assigned_to,status,category,created_at,sla_hours\n"
        "TKT-1002,API Gateway timeout,Slow response on external APIs,bob,Open,gateway,2026-06-09T10:05:00Z,4\n"
    )
    ticket_stream = io.StringIO(ticket_csv)

    result = agent1_data_collection.run(chat_stream, ticket_stream)

    # Assert basic structure
    assert "chats" in result
    assert "tickets" in result
    assert "all_incidents" in result
    assert "total_raw" in result

    # Check total counts
    assert result["total_raw"] == 2
    assert len(result["chats"]) == 1
    assert len(result["tickets"]) == 1

    # Check mapped fields for chat incident
    chat_inc = next(i for i in result["all_incidents"] if i["source"] == "chat")
    assert chat_inc["id"] == "CHAT-1001"
    assert chat_inc["title"] == "Database memory leak detected on production server."
    assert chat_inc["description"] == "Database memory leak detected on production server."
    assert chat_inc["agent"] == "alice"
    assert chat_inc["status"] == "Open"
    assert chat_inc["category"] == "database, prod"
    assert chat_inc["created_at"] == "2026-06-09T10:00:00Z"
    assert chat_inc["sla_hours"] is None

    # Check mapped fields for ticket incident
    tkt_inc = next(i for i in result["all_incidents"] if i["source"] == "ticket")
    assert tkt_inc["id"] == "TKT-1002"
    assert tkt_inc["title"] == "API Gateway timeout"
    assert tkt_inc["description"] == "Slow response on external APIs"
    assert tkt_inc["agent"] == "bob"
    assert tkt_inc["status"] == "Open"
    assert tkt_inc["category"] == "gateway"
    assert tkt_inc["created_at"] == "2026-06-09T10:05:00Z"
    assert tkt_inc["sla_hours"] == 4
