# Financial Analyst — Multi-Agent Text-to-SQL

A conversational financial analysis tool that translates natural language questions into SQL queries and returns data-driven answers. Built with a **multi-agent pipeline** where four specialized agents collaborate: planning, SQL generation, validation with self-correction, and response synthesis.

Runs **100% locally** — no API keys, no cloud dependencies. Powered by Llama 3.1 via Ollama.

## Demo

```
You:  "What's the total revenue by department in Q1?"

Plan: • Filter transactions where type = 'income' and date is between 2025-01-01 and 2025-03-31
      • Group by department and sum amounts

SQL:  SELECT department, SUM(amount) FROM transactions
      WHERE type = 'income' AND date BETWEEN '2025-01-01' AND '2025-03-31'
      GROUP BY department

Answer: Q1 revenue totals $1,139,000 across two departments:
        Sales generated $941,000 (83%) and Services contributed $198,000 (17%).
```

## Architecture

The system uses a **pipeline pattern** with four agents, each handling a single responsibility. The `Pipeline` orchestrator passes context between them and returns a structured `PipelineResult`.

```
User Question
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Pipeline (orchestrator)                                      │
│                                                               │
│   ┌──────────────┐                                           │
│   │ PlannerAgent  │  Interprets the question, decides what    │
│   │               │  data to retrieve (no SQL yet)            │
│   └──────┬───────┘                                           │
│          │ plan                                               │
│          ▼                                                    │
│   ┌──────────────┐                                           │
│   │  SQLAgent     │  Converts plan + schema into a            │
│   │               │  SQLite SELECT query                      │
│   └──────┬───────┘                                           │
│          │ sql                                                │
│          ▼                                                    │
│   ┌──────────────┐                                           │
│   │ValidatorAgent │  Executes the query. On error, feeds      │
│   │               │  the error back to the LLM for a fix.     │
│   │               │  Retries up to 3 times.                   │
│   └──────┬───────┘                                           │
│          │ columns, rows                                      │
│          ▼                                                    │
│   ┌──────────────┐                                           │
│   │ResponseAgent  │  Synthesizes a natural language answer     │
│   │               │  with dollar formatting and insights       │
│   └──────────────┘                                           │
│          │                                                    │
│          ▼                                                    │
│   PipelineResult(answer, plan, sql, raw_results, success)    │
└──────────────────────────────────────────────────────────────┘
```

### Why multi-agent over a single prompt chain?

| Concern | Single chain | Multi-agent pipeline |
|---|---|---|
| Prompt complexity | One massive prompt does everything | Each agent has a focused, short prompt |
| Error recovery | Fails on bad SQL, no retry | ValidatorAgent auto-corrects up to 3x |
| Debuggability | Black box | UI shows plan, SQL, and raw results per step |
| Swappability | Tightly coupled | Replace any agent independently (e.g., swap Ollama for OpenAI) |

## Project Structure

```
financial-analyst/
├── app.py                          # Streamlit UI (thin entrypoint)
├── src/
│   ├── config.py                   # Paths, model, URL, constants
│   ├── pipeline.py                 # Orchestrator + PipelineResult dataclass
│   │
│   ├── agents/
│   │   ├── planner_agent.py        # Question → retrieval plan
│   │   ├── sql_agent.py            # Plan + schema → SQL query
│   │   ├── validator_agent.py      # Execute → retry on error → results
│   │   └── response_agent.py       # Results → natural language answer
│   │
│   ├── prompts/
│   │   ├── planner_prompts.py      # System + user templates for planning
│   │   ├── sql_prompts.py          # SQL generation + error fix templates
│   │   └── response_prompts.py     # Response synthesis templates
│   │
│   └── tools/
│       ├── db_connector.py         # FinancialDatabase class (SQLite + CSV seeding)
│       └── llm.py                  # OllamaLLM wrapper
│
├── data/
│   └── sample_data.csv             # 42 financial transactions (Jan–Apr 2025)
│
├── tests/
│   └── test_pipeline.py            # Unit tests for database layer
│
├── requirements.txt
└── .gitignore
```

## Dataset

The sample dataset contains 42 synthetic financial transactions spanning January–April 2025:

| Field | Description | Examples |
|---|---|---|
| `date` | Transaction date (YYYY-MM-DD) | 2025-01-05, 2025-04-30 |
| `category` | Revenue or Expense | Revenue, Expense |
| `subcategory` | Specific type | Product Sales, Salaries, Cloud Infrastructure |
| `amount` | Always positive (USD) | 125000.00, 8500.00 |
| `type` | Direction | income, expense |
| `description` | Free-text detail | "Q1 software license sales" |
| `department` | Owning team | Sales, Engineering, HR, Marketing, Operations, Services, Legal |

**7 departments**, **2 categories**, **12 subcategories**, totaling ~$3.6M in transactions.

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running

### Install

```bash
git clone https://github.com/<your-username>/financial-analyst.git
cd financial-analyst

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

ollama pull llama3.1:8b
```

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501.

### Test

```bash
python -m unittest tests.test_pipeline -v
```

## Example Questions

- "What's the total revenue vs total expenses?"
- "Which department spends the most?"
- "Show me monthly income trends"
- "What are the top 3 expense subcategories?"
- "How much did we spend on cloud infrastructure in Q1?"
- "What percentage of revenue comes from subscriptions?"

## Stack

| Component | Technology | Purpose |
|---|---|---|
| LLM | Llama 3.1 8B (Ollama) | Planning, SQL generation, analysis |
| UI | Streamlit | Chat interface with expandable agent traces |
| Database | SQLite | Financial data store, seeded from CSV |
| Language | Python 3.10+ | Multi-agent orchestration |

## Design Decisions

- **Prompts separated from agents** — prompt templates live in `src/prompts/`, making them easy to iterate on without touching agent logic.
- **Schema injected into prompts** — the database schema is baked into SQL prompts so the LLM never guesses table or column names.
- **SELECT-only enforcement** — `db_connector.py` rejects any non-SELECT query before it reaches SQLite.
- **Stateless agents** — each agent is a pure function of its inputs. State lives only in the Streamlit session.
- **`@st.cache_resource`** — the pipeline, database, and LLM client are initialized once and reused across reruns.
