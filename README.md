# 🔄 AI-Powered Shift Continuity Platform

> **Shift Handover Note Generator** — An AI-powered system that reads chat logs and ticket data, removes duplicates, classifies priorities, predicts SLA risks, calculates a Shift Health Score, and generates a structured handover report.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/shift-continuity-platform.git
cd shift-continuity-platform
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama and download the Llama 3 model
This project runs entirely locally using Ollama with the Llama 3 model.
1. Download and install Ollama from [ollama.com](https://ollama.com).
2. Start the Ollama application.
3. Download the Llama 3 model using:
   ```bash
   ollama pull llama3
   ```
4. Verify the model runs locally:
   ```bash
   ollama run llama3
   ```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📁 Folder Structure

```
shift-continuity-platform/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── .env.example
├── README.md
│
├── agents/
│   ├── agent1_data_collection.py   # Reads + merges JSON & CSV
│   ├── agent2_deduplication.py     # Removes duplicate incidents
│   ├── agent3_classifier.py        # Classifies priority (Ollama + Llama 3)
│   ├── agent4_risk.py              # Predicts SLA risk (Ollama + Llama 3)
│   ├── agent5_health.py            # Calculates Health Score
│   └── agent6_report.py            # Generates handover report (Ollama + Llama 3)
│
├── utils/
│   └── ollama_client.py            # Centralised Ollama API wrapper
│
└── data/
    ├── chats.json                  # Sample chat logs
    └── tickets.csv                 # Sample ticket data
```

---

## 🤖 Agent Pipeline

```
Upload Files
     ↓
Agent 1: Data Collection  →  Merge JSON + CSV into unified incidents
     ↓
Agent 2: Deduplication    →  Remove near-duplicate incidents
     ↓
Agent 3: Classifier       →  Tag each incident: Critical / High / Medium / Low
     ↓
Agent 4: Risk Prediction  →  Predict SLA risk & escalation likelihood
     ↓
Agent 5: Health Score     →  Calculate 0–100 Shift Health Score
     ↓
Agent 6: Report Generator →  Generate structured Markdown handover report
```

---

## 📊 Output Format

The generated report includes:

| Section | Description |
|---|---|
| **Shift Health Score** | 0–100 score with grade (A–F) |
| **High Priority Issues** | Critical and High severity open items |
| **Risk Alerts** | Incidents flagged for SLA breach or escalation |
| **Completed Tasks** | Resolved incidents with resolution summary |
| **Watchlist** | Medium/Low items to monitor |
| **Recommended Actions** | 4–6 specific actions for the incoming shift |
| **Shift Summary** | Narrative overview of shift health |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| AI / LLM | Ollama + Llama 3 (Local) |
| Data processing | pandas |
| Deduplication | Python difflib |
| Environment config | python-dotenv |

---

## 📝 Sample Data

Sample files are provided in the `data/` folder:
- `data/chats.json` — 10 sample chat log entries
- `data/tickets.csv` — 10 sample support tickets

Use these to test the app immediately after setup.

---

## ⚙️ Configuration

No configuration or API keys are required as the platform runs entirely locally using Ollama.

---

## 🏆 AI Prototype Challenge

Built for the AI Prototype Challenge.  
**Project:** AI-Powered Shift Continuity Platform  
**Stack:** Python · Streamlit · Ollama + Llama 3 · Multi-Agent Architecture
