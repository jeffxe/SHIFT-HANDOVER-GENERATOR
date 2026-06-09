"""
AI-Powered Shift Continuity Platform
Shift Handover Note Generator
Run with: streamlit run app.py
"""

import streamlit as st
import requests
import pandas as pd
import altair as alt
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import agents
from agents import (
    agent1_data_collection,
    agent2_deduplication,
    agent3_classifier,
    agent4_risk,
    agent5_health,
    agent6_report,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SRE Shift Handover Dashboard",
    page_icon="🔄",
    layout="wide",
)

# Startup validation for Ollama
def check_ollama_health() -> bool:
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            return False
        models = response.json().get("models", [])
        model_names = [m.get("name") for m in models if m.get("name")]
        has_llama3 = any(name in ("llama3", "llama3:latest") or name.startswith("llama3:") for name in model_names)
        return has_llama3
    except Exception:
        return False

if not check_ollama_health():
    st.error("❌ Ollama is not running. Start Ollama and run: ollama run llama3")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
# Initialize session state for navigation and data storage
if "page" not in st.session_state:
    st.session_state["page"] = "upload"
if "sre_data" not in st.session_state:
    st.session_state["sre_data"] = None

# Custom CSS styling for premium SRE Black & Orange theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global Font Override */
html, body, [data-testid="stAppViewContainer"], .main {
    font-family: 'Outfit', sans-serif !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #111115 !important;
    border-right: 1px solid #FF6B0022 !important;
}

/* Global dividers */
hr {
    border-top: 2px solid #FF6B00 !important;
    opacity: 0.6;
}

/* Metric glassmorphism styling */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #15151A 0%, #1E1E24 100%) !important;
    border: 1px solid #FF6B001F !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 4px 25px rgba(0, 0, 0, 0.25) !important;
    transition: transform 0.3s ease, border-color 0.3s ease !important;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    border-color: #FF6B0066 !important;
}
div[data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    color: #FF6B00 !important;
}
div[data-testid="stMetricLabel"] {
    font-weight: 500 !important;
    color: #9CA3AF !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* File Uploader glassmorphism */
section[data-testid="stFileUploader"] {
    background-color: #15151A !important;
    border: 2px dashed #FF6B0022 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    transition: border-color 0.3s ease !important;
}
section[data-testid="stFileUploader"]:hover {
    border-color: #FF6B0077 !important;
}

/* Standard Buttons customization */
div.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Sidebar navigation button customization (Utility Secondary) */
section[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(135deg, #191922 0%, #24242E 100%) !important;
    color: #E5E7EB !important;
    border: 1px solid #FF6B0033 !important;
    font-size: 0.9rem !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: linear-gradient(135deg, #FF6B0011 0%, #FF6B0022 100%) !important;
    border-color: #FF6B00 !important;
    color: #FF6B00 !important;
}

/* Advanced Primary/Generate button customization */
div.stButton > button[kind="primary"], 
div.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #FF6B00 0%, #E63900 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #FF7B24 !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    padding: 16px 32px !important;
    border-radius: 10px !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 20px rgba(255, 107, 0, 0.35) !important;
    animation: generatePulse 2.5s infinite alternate !important;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(255, 107, 0, 0.55) !important;
    background: linear-gradient(135deg, #FF7B24 0%, #FF4D1A 100%) !important;
}
div.stButton > button[kind="primary"]:active,
div.stButton > button[data-testid="baseButton-primary"]:active {
    transform: translateY(1px) !important;
    box-shadow: 0 2px 10px rgba(255, 107, 0, 0.3) !important;
}

@keyframes generatePulse {
    0% {
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.3);
    }
    100% {
        box-shadow: 0 4px 25px rgba(255, 57, 0, 0.6);
    }
}

/* Advanced Download button customization */
div.stDownloadButton > button {
    background: linear-gradient(135deg, #111116 0%, #1B1B22 100%) !important;
    color: #FF6B00 !important;
    border: 2px solid #FF6B00 !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    padding: 16px 32px !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 20px rgba(255, 107, 0, 0.15) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    animation: downloadPulse 3s infinite alternate !important;
}
div.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #FF6B00 0%, #FF3D00 100%) !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 30px rgba(255, 107, 0, 0.45) !important;
    transform: translateY(-3px) !important;
}

@keyframes downloadPulse {
    0% {
        border-color: #FF6B00;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.15);
    }
    50% {
        border-color: #FF8C00;
        box-shadow: 0 4px 25px rgba(255, 140, 0, 0.35);
    }
    100% {
        border-color: #FF3D00;
        box-shadow: 0 4px 15px rgba(255, 61, 0, 0.15);
    }
}

/* Tabs list styling */
div[data-baseweb="tab-list"] {
    background-color: #15151A !important;
    padding: 6px !important;
    border-radius: 10px !important;
    border: 1px solid #FF6B0018 !important;
}
div[data-baseweb="tab-list"] button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #9CA3AF !important;
    border-radius: 6px !important;
    padding: 10px 18px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #FF6B001F !important;
    color: #FF6B00 !important;
}

/* Chatbot interface overrides */
div[data-testid="stChatMessage"] {
    background-color: #15151A !important;
    border: 1px solid #FF6B001A !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
}
div[data-testid="stChatMessage-assistant"] {
    border-left: 3px solid #FF6B00 !important;
}
div[data-testid="stChatMessage-user"] {
    border-left: 3px solid #3B82F6 !important;
}
/* Chat Input Container styling */
div[data-testid="stChatInput"] {
    background-color: #15151A !important;
    border: 1px solid #FF6B0022 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 25px rgba(0, 0, 0, 0.3) !important;
}
div[data-testid="stChatInput"] textarea {
    color: #F3F4F6 !important;
    font-family: 'Outfit', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar reset button on Dashboard page ─────────────────────────────────────
if st.session_state["page"] == "dashboard":
    with st.sidebar:
        st.header("⚙️ SRE Navigation")
        if st.button("🔄 Reset & Upload New Data", use_container_width=True):
            st.session_state["page"] = "upload"
            st.session_state["sre_data"] = None
            st.session_state.pop("chat_messages", None)
            st.rerun()

# ── Page 1: Upload Page ────────────────────────────────────────────────────────
if st.session_state["page"] == "upload":
    # Premium Page Title & Description Header
    st.markdown("""
    <div style="text-align: center; padding: 25px 0 45px 0;">
        <h1 style="font-weight: 800; font-size: 2.85rem; background: linear-gradient(90deg, #FF8C00 0%, #FF3D00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px; letter-spacing: -0.5px;">
            SRE Shift Continuity Platform
        </h1>
        <p style="font-size: 1.15rem; color: #9CA3AF; max-width: 650px; margin: 0 auto; line-height: 1.6;">
            Synthesize incident chat logs and ticket metrics into a unified, high-fidelity shift handover report. Powered by local Ollama & Llama 3.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Ingestion mode toggle using tabs
    tab_upload, tab_live = st.tabs(["📂 Manual File Upload", "🔌 Live Discord & Jira Sync"])

    run_pipeline = False
    chat_input_stream = None
    ticket_input_stream = None

    with tab_upload:
        # Ingestion portal card wrapper
        st.markdown("""
        <div style="background: linear-gradient(135deg, #15151A 0%, #1E1E24 100%); border: 1px solid #FF6B001A; border-radius: 16px; padding: 35px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35); margin-top: 10px;">
            <h3 style="color: #FF6B00; font-weight: 600; margin-top: 0; margin-bottom: 25px; font-size: 1.25rem; display: flex; align-items: center; gap: 8px; font-family: 'Outfit', sans-serif;">
                📂 SRE Manual Upload Ingestion
            </h3>
        """, unsafe_allow_html=True)
        
        col_chat, col_tkt = st.columns(2)
        with col_chat:
            chat_file = st.file_uploader("Chat Logs (JSON)", type=["json"])
        with col_tkt:
            ticket_file = st.file_uploader("Ticket Data (CSV)", type=["csv"])
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        generate_btn = st.button("⚡ Initialize AI Shift Continuity Engine", type="primary", use_container_width=True)
        
        if generate_btn:
            if not chat_file or not ticket_file:
                st.warning("⚠️ Please upload both a chat log (JSON) and a ticket file (CSV) before generating.")
            else:
                chat_input_stream = chat_file
                ticket_input_stream = ticket_file
                run_pipeline = True

    with tab_live:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #15151A 0%, #1E1E24 100%); border: 1px solid #FF6B001A; border-radius: 16px; padding: 35px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35); margin-top: 10px;">
            <h3 style="color: #FF6B00; font-weight: 600; margin-top: 0; margin-bottom: 25px; font-size: 1.25rem; display: flex; align-items: center; gap: 8px; font-family: 'Outfit', sans-serif;">
                🔌 Live Discord & Ticket API Sync
            </h3>
        """, unsafe_allow_html=True)
        
        col_api_chat, col_api_tkt = st.columns(2)
        with col_api_chat:
            st.markdown("##### 💬 Discord Configuration")
            disc_channel = st.text_input("Discord Channel ID", placeholder="e.g. 1152938475637284950")
            disc_token = st.text_input("Discord Bot Token", type="password", placeholder="Bot credentials (optional)")
            st.caption("Leave token blank to auto-sync SRE live message stream simulator.")
        with col_api_tkt:
            st.markdown("##### 🎫 Ticket System (Jira / ServiceNow)")
            jira_url = st.text_input("Jira Project URL / Endpoint", placeholder="e.g. https://company.atlassian.net/rest/api/3")
            jira_key = st.text_input("Jira API Token", type="password", placeholder="API key credentials (optional)")
            st.caption("Leave API key blank to auto-sync simulated incident backlog stream.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        sync_btn = st.button("🔌 Sync Live SRE Data & Analyze", type="primary", use_container_width=True)
        
        if sync_btn:
            with st.spinner("Executing live synchronization and payload conversion..."):
                try:
                    import io
                    from utils.live_ingestor import fetch_discord_chats, fetch_jira_tickets, convert_to_standard_formats
                    
                    # 1. Fetch live channels & databases
                    chats = fetch_discord_chats(disc_token, disc_channel)
                    tickets = fetch_jira_tickets(jira_url, jira_key)
                    
                    # 2. Automatically convert and format to JSON & CSV payloads
                    json_payload, csv_payload = convert_to_standard_formats(chats, tickets)
                    
                    # 3. Buffer into StringIO streams
                    chat_input_stream = io.StringIO(json_payload)
                    ticket_input_stream = io.StringIO(csv_payload)
                    run_pipeline = True
                except Exception as e:
                    st.error(f"Failed to synchronize live feeds: {e}")

    # Run SRE Pipeline
    if run_pipeline and chat_input_stream and ticket_input_stream:
        progress = st.progress(0, text="Initializing SRE analysis engine…")
        status   = st.empty()

        def update(step: int, total: int, msg: str):
            progress.progress(step / total, text=msg)
            status.info(f"🤖 {msg}")

        try:
            update(1, 5, "Parsing logs & merging ticket metadata databases...")
            data = agent1_data_collection.run(chat_input_stream, ticket_input_stream)

            update(2, 5, "Deduplicating duplicate alerts & resolving overlap...")
            data = agent2_deduplication.run(data)

            update(3, 5, "Running priority classification & evaluating SLA parameters...")
            data = agent3_classifier.run(data)

            update(4, 5, "Calculating shift health scores & SLA risk maps...")
            data = agent4_risk.run(data)
            data = agent5_health.run(data)

            update(5, 5, "Synthesizing SRE shift handover report...")
            data = agent6_report.run(data)

            # Generate PDF report bytes
            from utils.pdf_generator import markdown_to_pdf
            data["report_pdf"] = markdown_to_pdf(data.get("report_markdown", ""))

            progress.progress(1.0, text="✅ Handover complete!")
            status.success("✅ Handover report successfully generated!")
            
            # Save data and transition page
            st.session_state["sre_data"] = data
            st.session_state["page"] = "dashboard"
            st.rerun()

        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"❌ Handover pipeline error: {e}")
            st.exception(e)
            st.stop()

# ── Page 2: Dashboard Page ─────────────────────────────────────────────────────
elif st.session_state["page"] == "dashboard":
    data = st.session_state["sre_data"]
    
    # Premium Dashboard Title
    st.markdown("""
    <div style="padding: 10px 0 25px 0;">
        <h1 style="font-weight: 800; font-size: 2.25rem; background: linear-gradient(90deg, #FF8C00 0%, #FF3D00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px; letter-spacing: -0.3px;">
            🚨 Shift Continuity Dashboard
        </h1>
        <p style="font-size: 1.05rem; color: #9CA3AF; margin: 0;">
            Real-time operations intelligence, SLA risk predictors, and structured handover reports.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Metric cards ───────────────────────────────────────────────────────────
    score     = data["health_score"]
    grade     = data["health_grade"]
    breakdown = data["health_breakdown"]
    summary   = data.get("priority_summary", {})
    incidents = data["unique_incidents"]

    score_color = (
        "🟢" if score >= 75 else
        "🟡" if score >= 50 else
        "🔴"
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🏥 Health Score",     f"{score_color} {score}/100 ({grade})")
    col2.metric("📋 Unique Issues",    breakdown.get("total_incidents", 0))
    col3.metric("✅ Resolved",         breakdown.get("resolved", 0))
    col4.metric("🔓 Open",             breakdown.get("open", 0))
    col5.metric("🗑️ Duplicates Removed", data.get("total_duplicates", 0))

    # Deduplication Details
    total_dupes = data.get("total_duplicates", 0)
    if total_dupes > 0:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        with st.expander(f"🗑️ View Deduplication Audit Log ({total_dupes} duplicate alerts resolved)"):
            st.caption("The deduplication engine compares semantic similarity (threshold > 70%) to merge repeat alerts from chats and ticket sources.")
            table_md = "| Removed Duplicate Incident | Kept Master Incident | Similarity Score |\n| :--- | :--- | :---: |\n"
            for d in data.get("duplicates", []):
                table_md += f"| {d.get('removed')} | {d.get('kept')} | `{int(d.get('score', 0) * 100)}%` |\n"
            st.markdown(table_md)

    st.divider()

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_report, tab_metrics, tab_timeline, tab_explorer, tab_chat, tab_recs = st.tabs([
        "📄 Handover Report",
        "📈 Risk & Metrics",
        "⛓️ Chronological Timelines",
        "🔍 Incident Explorer",
        "💬 Assistant Q&A",
        "💡 AI Playbooks",
    ])

    # ── Tab 1: Report ──────────────────────────────────────────────────────────
    with tab_report:
        st.markdown(data.get("report_markdown", "_No report generated._"))
        st.divider()
        # Sole PDF Download button
        st.download_button(
            label="⬇️ Download Shift Handover Report (PDF)",
            data=data.get("report_pdf", b""),
            file_name="shift_handover_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # ── Tab 2: Risk & Metrics ──────────────────────────────────────────────────
    with tab_metrics:
        st.subheader("Operational Metrics Dashboard")
        
        # Calculate counts
        critical_count = sum(1 for i in incidents if i.get("priority") == "Critical")
        high_count     = sum(1 for i in incidents if i.get("priority") == "High")
        medium_count   = sum(1 for i in incidents if i.get("priority") == "Medium")
        low_count      = sum(1 for i in incidents if i.get("priority") == "Low")
        
        resolved_count = sum(1 for i in incidents if i.get("status") == "Resolved")
        mitigated_count = sum(1 for i in incidents if i.get("status") == "Mitigated")
        open_count     = sum(1 for i in incidents if i.get("status") not in ("Resolved", "Mitigated"))
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### Shift Risk Contributors")
            # Find open critical/high priority incidents or high SLA risk
            high_risk_incidents = [
                i for i in incidents 
                if i.get("status") != "Resolved" and (i.get("priority") in ("Critical", "High") or i.get("sla_risk") == "High Risk" or i.get("escalation_likely"))
            ]
            
            if high_risk_incidents:
                for i in high_risk_incidents:
                    st.warning(f"⚠️ Unresolved {i.get('priority')} Incident: {i.get('id')} - '{i.get('title')}'")
            else:
                st.success("✅ No critical unresolved risk contributors for this shift.")
                
        with col_right:
            st.markdown("### Incident Distribution")
            
            # Donut chart for severity breakdown
            st.markdown("**Severity Breakdown**")
            df_sev = pd.DataFrame([
                {"Severity": "Critical", "Count": critical_count},
                {"Severity": "High", "Count": high_count},
                {"Severity": "Medium", "Count": medium_count},
                {"Severity": "Low", "Count": low_count},
            ])
            df_sev = df_sev[df_sev["Count"] > 0]
            
            if not df_sev.empty:
                chart_donut = alt.Chart(df_sev).mark_arc(innerRadius=45).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Severity", type="nominal", scale=alt.Scale(
                        domain=["Critical", "High", "Medium", "Low"],
                        range=["#EF4444", "#F97316", "#EAB308", "#22C55E"]
                    )),
                    tooltip=["Severity", "Count"]
                ).properties(width=160, height=160)
                st.altair_chart(chart_donut, use_container_width=True)
            else:
                st.info("No incident severity data available.")
                
            # Bar chart for status counts
            st.markdown("**Incidents status counts**")
            df_status = pd.DataFrame([
                {"Status": "Resolved", "Count": resolved_count},
                {"Status": "Mitigated", "Count": mitigated_count},
                {"Status": "Open", "Count": open_count},
            ])
            df_status = df_status[df_status["Count"] > 0]
            
            if not df_status.empty:
                chart_bar = alt.Chart(df_status).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                    x=alt.X(field="Status", type="nominal", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y(field="Count", type="quantitative"),
                    color=alt.Color(field="Status", type="nominal", scale=alt.Scale(
                        domain=["Resolved", "Mitigated", "Open"],
                        range=["#10B981", "#3B82F6", "#EF4444"]
                    )),
                    tooltip=["Status", "Count"]
                ).properties(height=160)
                st.altair_chart(chart_bar, use_container_width=True)
            else:
                st.info("No status data available.")

    # ── Tab 3: Chronological Timelines ──────────────────────────────────────────
    with tab_timeline:
        st.subheader("Chronological Incident Timeline")
        sorted_incidents = sorted(
            incidents,
            key=lambda x: x.get("created_at", "") or ""
        )
        
        timeline_html = """
        <div style="position: relative; padding-left: 25px; border-left: 2px solid #FF6B0033; margin-top: 25px; margin-bottom: 25px; font-family: 'Outfit', sans-serif;">
        """
        for inc in sorted_incidents:
            timestamp = inc.get("created_at") or "Unknown Time"
            priority = inc.get("priority", "Medium")
            p_color = (
                "#EF4444" if priority == "Critical" else
                "#F97316" if priority == "High" else
                "#EAB308" if priority == "Medium" else
                "#22C55E"
            )
            status = inc.get("status", "Open")
            s_bg = "#10B9811C" if status == "Resolved" else "#3B82F61C" if status == "Mitigated" else "#EF44441C"
            s_color = "#10B981" if status == "Resolved" else "#3B82F6" if status == "Mitigated" else "#EF4444"
            
            timeline_html += f"""
            <div style="position: relative; margin-bottom: 24px;">
                <!-- Timeline Dot -->
                <div style="position: absolute; left: -32px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background-color: {p_color}; border: 3px solid #0B0B0E; box-shadow: 0 0 8px {p_color}88;"></div>
                
                <div style="background: linear-gradient(135deg, #15151A 0%, #1E1E24 100%); border: 1px solid #FF6B0011; border-radius: 10px; padding: 16px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                        <span style="font-size: 0.85rem; color: #9CA3AF; font-weight: 500;">⏱️ {timestamp}</span>
                        <span style="background-color: {s_bg}; color: {s_color}; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.5px;">{status}</span>
                    </div>
                    <h4 style="margin: 0 0 6px 0; color: #FFFFFF; font-size: 1rem; font-weight: 600; font-family: 'Outfit', sans-serif;">
                        <span style="color: {p_color}; font-weight: 700;">[{inc.get('id')}]</span> {inc.get('title')}
                    </h4>
                    <div style="display: flex; gap: 15px; font-size: 0.85rem; color: #9CA3AF;">
                        <span>Owner: <strong style="color: #E5E7EB;">{inc.get('agent', 'Unassigned')}</strong></span>
                        <span>•</span>
                        <span>Priority: <strong style="color: {p_color};">{priority}</strong></span>
                    </div>
                </div>
            </div>
            """
        timeline_html += "</div>"
        # Clean leading/trailing spaces from each line to prevent Streamlit's markdown parser from treating it as preformatted code
        cleaned_timeline_html = "\n".join(line.strip() for line in timeline_html.splitlines())
        st.markdown(cleaned_timeline_html, unsafe_allow_html=True)

    # ── Tab 4: Incident Explorer ───────────────────────────────────────────────
    with tab_explorer:
        st.subheader("Incident Explorer")
        
        # Search bar
        search_query = st.text_input("🔍 Search incidents by title, ID, description, or owner...", "")
        
        # Filters
        c_prio, c_status = st.columns(2)
        prio_filter = c_prio.multiselect("Filter by Priority", ["Critical", "High", "Medium", "Low"])
        status_filter = c_status.multiselect("Filter by Status", list(set(i.get("status", "Open") for i in incidents)))
        
        filtered = incidents
        if search_query:
            q = search_query.lower()
            filtered = [
                i for i in filtered
                if q in i.get("title", "").lower() or q in i.get("id", "").lower() or q in i.get("description", "").lower() or q in i.get("agent", "").lower()
            ]
        if prio_filter:
            filtered = [i for i in filtered if i.get("priority") in prio_filter]
        if status_filter:
            filtered = [i for i in filtered if i.get("status") in status_filter]
            
        st.markdown(f"Found **{len(filtered)}** incident(s)")
        
        for inc in filtered:
            priority_icon = "🔴" if inc.get("priority") == "Critical" else "🟠" if inc.get("priority") == "High" else "🟡" if inc.get("priority") == "Medium" else "🟢"
            exp_title = f"{priority_icon} [{inc.get('priority')}] {inc.get('id')} — {inc.get('title')} — {inc.get('status')}"
            with st.expander(exp_title):
                st.markdown(f"**Assigned SRE:** {inc.get('agent', 'Unassigned')}")
                st.markdown(f"**Description:** {inc.get('description')}")
                if inc.get("priority_reason"):
                    st.caption(f"Priority reason: {inc['priority_reason']}")
                if inc.get("risk_reason"):
                    st.caption(f"Risk reason: {inc['risk_reason']}")

    # ── Tab 5: Assistant Q&A ───────────────────────────────────────────────────
    with tab_chat:
        st.subheader("Chat with Shift Assistant")
        st.caption("Ask the AI chatbot details about ownership, unresolved incidents, status adjustments, or timeline histories.")
        
        # Chat history in session state
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {"role": "assistant", "content": "Hi! I am your SRE Shift Handover Assistant. Ask me anything about this shift! For example: 'What issues are still open?', 'Who owns TKT-1001?', or 'Show me a summary of what changed.'"}
            ]
        
        # Render messages
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Chat input
        if user_query := st.chat_input("Ask a question about the shift..."):
            # User message
            with st.chat_message("user"):
                st.write(user_query)
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            
            # Generate answer using Ollama Llama 3
            with st.chat_message("assistant"):
                with st.spinner("Analyzing shift context..."):
                    # Build summary data
                    compact_incidents = [
                        {
                            "id": i.get("id"),
                            "title": i.get("title"),
                            "status": i.get("status"),
                            "priority": i.get("priority"),
                            "agent": i.get("agent"),
                            "sla_risk": i.get("sla_risk"),
                            "escalation": i.get("escalation_likely"),
                            "description": i.get("description", "")[:150]
                        }
                        for i in incidents
                    ]
                    context = {
                        "health_score": data.get("health_score"),
                        "health_grade": data.get("health_grade"),
                        "incidents": compact_incidents
                    }
                    chat_prompt = f"""
                    You are a helpful SRE Shift Handover Assistant. Answer the SRE team's question based strictly on the current shift data below.
                    Be concise, direct, and professional.
                    
                    Shift Data:
                    {json.dumps(context, indent=2)}
                    
                    Question: {user_query}
                    """
                    # Import call_ollama dynamically
                    from utils.ollama_client import call_ollama
                    response = call_ollama(chat_prompt, num_predict=512)
                    st.write(response)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": response})

    # ── Tab 6: AI Playbooks ───────────────────────────────────────────────────
    with tab_recs:
        st.subheader("💡 SRE AI Resolution Playbooks")
        st.caption("Generate a dynamic, structured resolution playbook and escalation path for the unresolved critical and high priority incidents in this shift.")
        
        # Check if recommendations are already in session state
        if "sre_recommendations" not in st.session_state:
            st.session_state["sre_recommendations"] = None
            
        # Button to trigger recommendation generation
        rec_btn = st.button("⚡ Generate SLA Recovery Playbook", use_container_width=True)
        
        if rec_btn:
            with st.spinner("Analyzing unresolved incidents and generating playbooks..."):
                # Get unresolved critical and high priority incidents
                unresolved = [
                    i for i in incidents 
                    if i.get("status", "").lower() not in ("resolved", "mitigated") and i.get("priority") in ("Critical", "High")
                ]
                
                if not unresolved:
                    st.session_state["sre_recommendations"] = "### ✅ All Critical and High incidents are resolved!\nNo recovery playbooks required."
                else:
                    open_summary = [
                        {
                            "id": i.get("id"),
                            "title": i.get("title"),
                            "priority": i.get("priority"),
                            "category": i.get("category"),
                            "description": i.get("description", "")[:200]
                        }
                        for i in unresolved
                    ]
                    
                    recs_prompt = f"""
                    You are a Principal SRE and Support Operations Architect.
                    Based on the open incidents from the shift, generate a structured SRE Recovery Playbook.
                    
                    Open Incidents:
                    {json.dumps(open_summary, indent=2)}
                    
                    For each incident:
                    1. Highlight a 3-step mitigation playbook (Triage, Workaround, Resolution).
                    2. List the assigned action items.
                    3. Recommend a specific escalation path.
                    
                    Keep the response concise, clean, and highly technical. Use Markdown headers and code blocks where appropriate. Do not include introductory text.
                    """
                    from utils.ollama_client import call_ollama
                    recs_response = call_ollama(recs_prompt, num_predict=1536)
                    st.session_state["sre_recommendations"] = recs_response
            st.rerun()
            
        if st.session_state["sre_recommendations"]:
            st.markdown(st.session_state["sre_recommendations"])

