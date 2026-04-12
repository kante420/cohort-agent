<p align="center">
  <img src="text_logo.png"/>
</p>

<h1 align="center"></h1>

### Designed for Dedalus Dathathon Castilla-La Mancha

The challenge of this project lies on indentifying cohorts of cronic patients based on a conversational agent.

---

## What it does

Síntoma SELECT lets healthcare professionals query clinical data in plain Spanish — no SQL knowledge required. Ask questions like:

- *"How many patients have diabetes and hypertension?"*
- *"What is the average age per province?"*
- *"Which medications does patient 5 take?"*
- *"How many procedures were performed in 2024?"*

The agent translates each question into SQL, executes it against a DuckDB database, and returns a natural language answer with automatic charts.

---

**Key components:**

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph |
| LLM | Qwen 2.5 Coder 14B Q8 via Ollama |
| Database | DuckDB (6 CSV cohort files) |
| Visualization | Plotly |
| UI | Streamlit |

---

## Getting started

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com/download) installed and running
- The 6 cohort CSV files (provided separately)
---

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/kante420/cohort-agent.git
cd cohort-agent
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Pull the LLM model**
```bash
ollama pull qwen2.5-coder:14b-instruct-q8_0
```

> For lower-end machines, `qwen2.5-coder:7b` also works.

**5. Configure environment**

Create a `.env` file in the project root:

> DB_PATH=./db/cohort.duckdb

> OLLAMA_HOST=http://localhost:11434

> If using a remote GPU (e.g. Google Cloud), replace `localhost` with the external IP of your instance.

**6. Add the cohort CSV files**

Place the 6 CSV files inside `data/raw/`

**7. Load the database**
```bash
python -m db.setup
```

**8. Launch the app**
```bash
streamlit run app.py
```

The app runs at `http://localhost:8501` by default.

---

## Features

- **Natural language to SQL** — automatic translation with hallucination prevention
- **Smart routing** — intent detection directs each query to the right node
- **Auto charts** — bar, pie, area and histogram generated from query results
- **Session memory** — conversation history including previous SQL for context
- **Quick actions** — sidebar lookup by patient ID (medication, medical history)
- **Export** — download results as CSV or full conversation as PDF
- **Remote GPU support** — connect to Ollama running on Google Cloud, vast.ai, etc.

---

## Built by

**Hugo Cantero Serrano** · 2nd year Computer Engineering · ESIIAB, UCLM  
**Diego Calcerrada Romero** · 2nd year Computer Engineering · ESIICR, UCLM

