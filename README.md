# Hooli Heard

**Voice of Customer intelligence platform** — consolidates customer signals from Gong, Salesforce, Jira, Slack, and Qualtrics into structured, prioritized, and visualized product feature requirements.

Built for the CoreWeave "More. Faster. Better. 2026" hackathon.

## Team

- Urvashi Chowdhary
- Brian Leong
- Olya Sukhorukova
- Rafael Suguiura
- Brett Cristino

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Frontend | React, TypeScript, Tailwind CSS, Vite |
| Database | PostgreSQL 16 |
| Charts | Recharts |
| State | TanStack Query + URL search params |
| LLM | Claude API (Anthropic SDK) |
| Infra | docker-compose |

## Architecture

```
Source Signals          Synthesize           Normalize            Visualize
─────────────          ──────────           ─────────            ─────────
Gong (calls)     ──┐                    ┌── Roadmap/NPI     ┌── Dashboard
Salesforce (CRM) ──┤   Claude API       │── Jira backlog    ├── Insights
Jira CFR         ──┼── Extract ──────── ┤── OKR alignment   ├── Lineage
Slack            ──┤   Classify                              ├── Reports
Qualtrics        ──┘   Dedup                                 └── Actions
```

**4-Stage Pipeline:**
1. **Ingest** — Pull raw signals from 5 sources
2. **Synthesize** — Claude extracts insights, classifies by product area (5) and category (13), deduplicates
3. **Normalize** — Map to roadmap items, backlog, OKRs
4. **Visualize** — Exec dashboard, drill-down insights, source lineage

## Quick Start

### Prerequisites

- PostgreSQL 16
- Python 3.9+
- Node.js 18+

### Setup

```bash
# 1. Create database
createuser hooli
createdb -O hooli hooliheard
psql -d hooliheard -c "GRANT ALL ON SCHEMA public TO hooli;"

# 2. Install backend dependencies
pip3 install fastapi 'uvicorn[standard]' sqlalchemy psycopg2-binary anthropic pydantic-settings python-dotenv

# 3. Install frontend dependencies
make frontend-install

# 4. Start backend (terminal 1)
make backend-dev

# 5. Seed database with real insights (terminal 2)
export DATABASE_URL=postgresql://hooli@localhost:5432/hooliheard
python3 scripts/seed_db.py

# 6. Start frontend (terminal 3)
make frontend-dev
```

Open **http://localhost:5173**

### With Docker

```bash
cp .env.example .env   # configure API keys
make up                 # starts Postgres + backend
make seed               # load insights
make frontend-dev       # start frontend
```

## Data Pipeline

### Pull real data (via MCP/Glean)

The pipeline pulls from 4 connected sources:

| Source | Records | Method |
|--------|---------|--------|
| Jira CFR | 95 | Atlassian MCP (`project = CFR`) |
| Gong | 25 | Glean search (`app: gong`) |
| Salesforce | 31 | Glean search (`app: salescloud`) |
| Slack | 12 | Glean search (`app: slack`) |

### Synthesize

```bash
# Normalize raw data into unified format
python3 scripts/normalize_raw.py

# Extract and classify insights (rule-based, no API key needed)
python3 scripts/synthesize_local.py

# Or use Claude API for higher quality extraction
export ANTHROPIC_API_KEY=sk-ant-...
python3 scripts/synthesize.py
```

**Output:** `data/output/insights.json` — 210 insights (136 key records, 74 duplicates)

## Product Taxonomy

### Product Areas
- **Infra** — Compute, Storage, Networking
- **CKS** — BMaaS, CKS, Consumption Models
- **Platform** — Security & Compliance, Console/API/Terraform, Observability
- **AI Services** — SUNK/Training, Inference, RL/Evals
- **W&B** — Weights & Biases

### Insight Categories
Capacity | Capacity Issues | Pricing/Terms | Enhancement | Blocker | Issues | Education Gaps | Product Fit/Scope | Competition/Alternatives | GTM/Partnership | Success Pattern | Process/Operational Friction | Null

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check with DB connectivity |
| `GET /api/insights` | Paginated insights with filters |
| `GET /api/insights/{id}` | Single insight detail |
| `GET /api/insights/export` | CSV export |
| `GET /api/dashboard/summary` | Total insights, key records, accounts, sources |
| `GET /api/dashboard/by-area` | Counts by product area |
| `GET /api/dashboard/by-category` | Counts by insight category |
| `GET /api/dashboard/by-account` | Top accounts by insight volume |
| `GET /api/dashboard/trend` | Weekly time series |
| `GET /api/accounts` | Account list with insight counts |
| `GET /api/accounts/{name}` | Account detail + insights |

All dashboard endpoints support filters: `product_area`, `insight_category`, `account_name`, `date_from`, `date_to`

## Project Structure

```
hooli-heard/
├── backend/
│   └── app/
│       ├── api/           # FastAPI route handlers
│       ├── models/        # SQLAlchemy models
│       ├── schemas/       # Pydantic request/response models
│       ├── services/      # Business logic
│       ├── config.py      # Pydantic settings
│       ├── db.py          # Database engine + session
│       └── main.py        # FastAPI app entry point
├── frontend/
│   └── src/
│       ├── api/           # Typed API clients
│       ├── components/    # React components (dashboard, insights, shared)
│       ├── hooks/         # TanStack Query hooks
│       ├── lib/           # Constants, utilities
│       └── types/         # TypeScript interfaces
├── scripts/
│   ├── pull_*.py          # Source data pull scripts
│   ├── normalize_raw.py   # Data normalizer
│   ├── synthesize.py      # Claude API synthesis
│   ├── synthesize_local.py # Rule-based synthesis
│   └── seed_db.py         # Database seeder
├── data/
│   ├── raw/               # Raw pulled data (JSON)
│   ├── output/            # Synthesized insights (JSON/CSV)
│   ├── prompts/           # Claude extraction prompt
│   └── taxonomy.json      # Product area + category definitions
├── docker-compose.yml
├── Makefile
└── CLAUDE.md
```

## License

Internal CoreWeave hackathon project.
