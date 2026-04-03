# AI Marketing Agency MVP

A fully modular, end-to-end AI marketing agency system built with **CrewAI + GPT-4o + Streamlit**.

Enter a client brief once. Seven specialised AI agents produce production-ready outputs:
strategy, copy, media plan, funnel spec, automations, creative briefs, and a project plan.

---

## Project Structure

```
ai-agency-mvp/
│
├── app.py                  # Streamlit entry point (thin orchestrator)
├── crew.py                 # CrewAI Crew builder + runner
├── requirements.txt
├── .env.example            # Copy to .env and add your key
│
├── config/
│   ├── __init__.py
│   └── settings.py         # All env vars loaded here — single source of truth
│
├── agents/
│   ├── __init__.py
│   ├── llm.py              # Shared GPT-4o factory
│   ├── strategist.py
│   ├── copywriter.py
│   ├── media_buyer.py
│   ├── funnel_builder.py
│   ├── automation_builder.py
│   ├── creative_director.py
│   └── project_manager.py
│
├── tasks/
│   ├── __init__.py
│   ├── models.py           # ClientInput dataclass
│   └── builder.py          # All 7 Task objects with context chaining
│
├── database/
│   ├── __init__.py
│   ├── connection.py       # SQLite connection factory
│   ├── schema.py           # Table creation
│   └── repository.py       # All read/write functions
│
├── ghl/
│   ├── __init__.py
│   └── formatter.py        # Mock GHL payload + production stub
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py          # Past clients sidebar
│   ├── input_form.py       # New client brief form + crew runner
│   └── output_view.py      # Per-agent output tabs + download
│
└── utils/
    ├── __init__.py
    └── helpers.py          # extract_task_outputs, Timer, format_duration
```

---

## Quick Start

### 1. Clone / create the project folder
```bash
mkdir ai-agency-mvp && cd ai-agency-mvp
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your environment file
```bash
cp .env.example .env
```
Open `.env` and add your **OpenAI API key**:
```
OPENAI_API_KEY=sk-your-key-here
```

### 5. Run the app
```bash
streamlit run app.py
```

Your browser opens at **http://localhost:8501** automatically.

---

## How It Works

| Step | What happens |
|------|-------------|
| You fill the form | Business name, offer, audience, positioning, goals, budget, situation |
| FastAPI receives it | `ClientInput` dataclass validates the data |
| CrewAI runs 7 agents | Sequential: Strategist → Copywriter → Media Buyer → Funnel Builder → Automation Builder → Creative Director → Project Manager |
| Outputs saved | SQLite stores everything keyed by client |
| Dashboard displays | 7 tabs — one per agent — plus Mock GHL payload |
| Download | Full JSON export with one click |

---

## Agent Pipeline

```
ClientInput
    │
    ▼
1. Strategist        ──► strategy doc (feeds everyone below)
    │
    ├──► 2. Copywriter      ──► ads, emails, landing page, sales page
    │
    ├──► 3. Media Buyer     ──► Meta campaign structure, ad sets, budgets
    │
    │    [Copy + Media]
    │         │
    ▼         ▼
4. Funnel Builder    ──► GHL funnel spec (page-by-page)
    │
    ▼
5. Automation Builder ──► GHL workflows, nurture, pipeline rules
    │
    [Copy + Media]
    │
    ▼
6. Creative Director  ──► 3 ad creative briefs + Midjourney prompts
    │
    [All above]
    │
    ▼
7. Project Manager    ──► phased task plan with owners + deadlines
```

---

## Upgrading to Production

### Swap SQLite → Supabase / Postgres
Edit `database/connection.py` — replace `sqlite3.connect()` with a Postgres connection.
No other file changes needed.

### Connect live GHL API
Edit `ghl/formatter.py` — implement the `push_to_ghl()` stub with real REST calls.
Add `GHL_API_KEY` and `GHL_LOCATION_ID` to your `.env`.

### Swap model
Edit `.env`:
```
OPENAI_MODEL=gpt-4-turbo   # or any other supported model
```

---

## Requirements

- Python 3.11+
- OpenAI API key with GPT-4o access
- ~3–6 minutes per client run (7 sequential LLM calls)
