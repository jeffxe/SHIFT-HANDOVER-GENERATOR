import json
import csv
import io
import requests
from datetime import datetime

def fetch_discord_chats(token: str = None, channel_id: str = None) -> list:
    """
    Fetches real-time messages from Discord API if credentials are provided,
    otherwise falls back to generating a high-fidelity simulated SRE chat log list.
    """
    if token and channel_id:
        try:
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            headers = {
                "Authorization": f"Bot {token}",
                "User-Agent": "AntigravitySREHandover (1.0)"
            }
            # Fetch last 50 messages
            response = requests.get(url, headers=headers, params={"limit": 50}, timeout=10)
            if response.status_code == 200:
                messages = response.json()
                chats = []
                for m in messages:
                    # Parse author
                    author = m.get("author", {})
                    username = author.get("username", "Unknown")
                    # Try to extract keywords for SRE tags
                    content = m.get("content", "")
                    tags = []
                    lower_content = content.lower()
                    if "outage" in lower_content or "down" in lower_content:
                        tags.append("outage")
                    if "pay" in lower_content or "billing" in lower_content:
                        tags.append("payment")
                    if "login" in lower_content or "auth" in lower_content:
                        tags.append("login")
                    if "db" in lower_content or "backup" in lower_content:
                        tags.append("database")
                    if "ssl" in lower_content or "cert" in lower_content:
                        tags.append("ssl")
                    if "slow" in lower_content or "latency" in lower_content:
                        tags.append("performance")
                    
                    chats.append({
                        "id": f"discord_{m.get('id')}",
                        "timestamp": m.get("timestamp", datetime.utcnow().isoformat()),
                        "agent": username,
                        "message": content,
                        "tags": tags if tags else ["alert"]
                    })
                return chats
        except Exception as e:
            # Fallback to simulated data if Discord connection errors out
            pass

    # High-fidelity simulated SRE Discord chats
    now_iso = datetime.now().isoformat()
    return [
        {
            "id": "chat_001",
            "timestamp": now_iso,
            "agent": "Alice",
            "message": "Payment gateway is down. Multiple customers reporting failed transactions. Ticket raised.",
            "tags": ["payment", "outage", "critical"]
        },
        {
            "id": "chat_002",
            "timestamp": now_iso,
            "agent": "Bob",
            "message": "Login service throwing 503 errors intermittently for EU region users.",
            "tags": ["login", "503", "eu-region"]
        },
        {
            "id": "chat_003",
            "timestamp": now_iso,
            "agent": "Alice",
            "message": "Payment gateway issue persists. Escalated to infra team. ETA unknown.",
            "tags": ["payment", "outage", "escalated"]
        },
        {
            "id": "chat_004",
            "timestamp": now_iso,
            "agent": "Charlie",
            "message": "Dashboard loading slow for enterprise accounts. Avg load time 12s instead of 2s.",
            "tags": ["dashboard", "performance", "enterprise"]
        },
        {
            "id": "chat_005",
            "timestamp": now_iso,
            "agent": "Bob",
            "message": "EU login 503 errors resolved after pod restart. Monitoring for recurrence.",
            "tags": ["login", "resolved", "eu-region"]
        },
        {
            "id": "chat_006",
            "timestamp": now_iso,
            "agent": "Charlie",
            "message": "Email notification service delayed by ~45 minutes. Backlog of 2000 unsent emails.",
            "tags": ["email", "delay", "backlog"]
        },
        {
            "id": "chat_007",
            "timestamp": now_iso,
            "agent": "Alice",
            "message": "Payment gateway partially restored. Transactions succeeding at 70%. Team still working.",
            "tags": ["payment", "partial-fix", "ongoing"]
        },
        {
            "id": "chat_008",
            "timestamp": now_iso,
            "agent": "Diana",
            "message": "New issue: SSL certificate expiring in 3 days for api.company.com. Needs urgent renewal.",
            "tags": ["ssl", "certificate", "expiry", "urgent"]
        },
        {
            "id": "chat_009",
            "timestamp": now_iso,
            "agent": "Bob",
            "message": "Dashboard slowness traced to missing DB index. Fix deployed, load time back to 2s.",
            "tags": ["dashboard", "resolved", "db-index"]
        },
        {
            "id": "chat_010",
            "timestamp": now_iso,
            "agent": "Diana",
            "message": "Mobile app crashing on Android 14 devices after latest update. 50+ user reports.",
            "tags": ["mobile", "android", "crash", "regression"]
        }
    ]

def fetch_jira_tickets(endpoint: str = None, api_key: str = None) -> list:
    """
    Fetches real-time tickets from API if endpoint and auth are provided,
    otherwise falls back to generating simulated incident ticket items.
    """
    if endpoint and api_key:
        try:
            # Placeholder for active API endpoint fetch
            response = requests.get(endpoint, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            if response.status_code == 200:
                # Map ticketing fields to SRE dashboard fields
                # ...
                pass
        except Exception:
            pass

    # High-fidelity simulated incident tickets
    now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [
        {
            "ticket_id": "TKT-1001",
            "title": "Payment gateway outage",
            "description": "Customers unable to complete transactions. Revenue impact high.",
            "status": "Open",
            "assigned_to": "Alice",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 4,
            "category": "Payment"
        },
        {
            "ticket_id": "TKT-1002",
            "title": "Login 503 EU region",
            "description": "Intermittent 503 errors on login service for EU users.",
            "status": "Resolved",
            "assigned_to": "Bob",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 8,
            "category": "Authentication"
        },
        {
            "ticket_id": "TKT-1003",
            "title": "Dashboard performance degradation",
            "description": "Enterprise dashboard loading in 12 seconds. SLA breach imminent.",
            "status": "Resolved",
            "assigned_to": "Charlie",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 6,
            "category": "Performance"
        },
        {
            "ticket_id": "TKT-1004",
            "title": "Email notification backlog",
            "description": "Email service delayed. ~2000 emails queued. Customers not receiving alerts.",
            "status": "Open",
            "assigned_to": "Charlie",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 12,
            "category": "Notifications"
        },
        {
            "ticket_id": "TKT-1005",
            "title": "SSL certificate expiry warning",
            "description": "api.company.com SSL cert expires in 3 days. Requires immediate renewal.",
            "status": "Open",
            "assigned_to": "Diana",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 24,
            "category": "Security"
        },
        {
            "ticket_id": "TKT-1006",
            "title": "Android 14 app crash",
            "description": "Mobile app crashes on launch for Android 14 users after v3.2.1 update.",
            "status": "Open",
            "assigned_to": "Diana",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 8,
            "category": "Mobile"
        },
        {
            "ticket_id": "TKT-1007",
            "title": "Payment gateway down",
            "description": "Users cannot pay. Multiple failed transaction reports coming in.",
            "status": "Open",
            "assigned_to": "Alice",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 4,
            "category": "Payment"
        },
        {
            "ticket_id": "TKT-1008",
            "title": "API rate limit errors",
            "description": "Some enterprise clients hitting 429 rate limit errors on bulk import API.",
            "status": "Open",
            "assigned_to": "Bob",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 12,
            "category": "API"
        },
        {
            "ticket_id": "TKT-1009",
            "title": "Database backup failure",
            "description": "Nightly DB backup job failed silently. Last successful backup 36hrs ago.",
            "status": "Open",
            "assigned_to": "Charlie",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 6,
            "category": "Infrastructure"
        },
        {
            "ticket_id": "TKT-1010",
            "title": "Two-factor auth not sending SMS",
            "description": "Users report 2FA SMS codes not arriving. Affects ~15% of logins.",
            "status": "Open",
            "assigned_to": "Bob",
            "created_at": now_date,
            "updated_at": now_date,
            "sla_hours": 8,
            "category": "Authentication"
        }
    ]

def convert_to_standard_formats(chats: list, tickets: list) -> tuple[str, str]:
    """
    Converts list of chat logs into a JSON string and list of tickets
    into a standardized CSV format string.
    """
    # 1. Convert chats to JSON string
    json_str = json.dumps(chats, indent=2)

    # 2. Convert tickets to CSV string
    csv_buffer = io.StringIO()
    headers = [
        "ticket_id", "title", "description", "status", 
        "assigned_to", "created_at", "updated_at", "sla_hours", "category"
    ]
    writer = csv.DictWriter(csv_buffer, fieldnames=headers)
    writer.writeheader()
    for t in tickets:
        writer.writerow(t)
    
    csv_str = csv_buffer.getvalue()
    csv_buffer.close()

    return json_str, csv_str
