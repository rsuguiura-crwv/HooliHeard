# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Hooli Heard is a hackathon project ("More. Faster. Better. 2026") that builds agentic intelligence
to funnel diverse customer signals into structured, prioritized, and visualized product feature
requirements for data-driven product prioritization and roadmap execution.

## Team

- Urvashi Chowdhary
- Brian Leong
- Olya Sukhorukova
- Rafael Suguiura
- Brett Cristino

## Tech Stack

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Database**: PostgreSQL 16
- **LLM**: Claude API (Anthropic SDK) for insight extraction + classification
- **Charts**: Recharts
- **State**: TanStack Query (React Query) + URL search params for filters
- **Infra**: docker-compose (Postgres + backend + frontend)

## Architecture — 4-Stage Pipeline

### Stage 1: Input Data (Ingestion)
Pull raw customer signals from multiple sources and normalize to a common schema.

**MVP — continuous inputs:**
- Sales conversations / Voice of Field (Gong)
- SA insights / Customer Requests (Jira CRs)
- Support friction (tickets)
- Sales pipeline context / closed-loss insights (Salesforce)

**MVP — initiative-based inputs:**
- Direct customer feedback (surveys, CAB via Qualtrics)

**Longer term (post-hackathon):**
- Annual CSAT satisfaction
- Product usage/adoption data

Sources: Gong, Slack, Jira, Salesforce, Qualtrics, Transcripts/Excel

### Stage 2: Synthesize (Enrichment)
AI-powered processing of raw signals via Claude API:
1. Dedupe information across sources
2. Tag items by product type (5 product areas, subcategories)
3. Categorize by feedback type (13 insight categories)
4. Weight by customer type (enterprise vs. SMB, etc.)
5. Prioritize by frequency/urgency

### Stage 3: Normalize
Map synthesized insights into existing business constructs:
1. Roadmap — NPI (New Product Introduction)
2. Jira — backlog items
3. OKRs alignment

### Stage 4: Visualize / Action
App layer for stakeholders:
1. Dashboard — Exec view
2. Insights — drill-down analysis
3. Lineage — trace backlog items back to source signals
4. Reporting — summaries and exports
5. Actions — create Jira tickets, update roadmap

## Implementation Phases

1. **Data Pulls + Sample Output Review** — Standalone scripts pull from each source, Claude synthesizes, output CSV for team review. No DB/app yet.
2. **Foundation** — PostgreSQL schema, FastAPI backend, React frontend scaffold, docker-compose.
3. **API + Dashboard** — REST API endpoints, exec dashboard with charts and filters.
4. **Live Pipeline** — Integrate connectors + Claude synthesis into unified pipeline runner.
5. **Polish + Demo** — Lineage page, Jira actions, visual polish, demo dataset.

See full plan: `.claude/plans/adaptive-wobbling-sonnet.md`

### Key Directories

- `scripts/` — Standalone data pull scripts (Phase 1) and utilities
- `data/` — Taxonomy definitions, raw pulled data, sample output, schema
- `backend/` — FastAPI app, SQLAlchemy models, connectors, synthesize, pipeline
- `frontend/` — React + TypeScript + Tailwind app (dashboard, insights, lineage)

## Key References

- [Data Schema Spreadsheet](https://docs.google.com/spreadsheets/d/1IHDLh47L7fgr7HfiTPzvim2NI6pUB__VSUtT7oeNUPk/edit?gid=0#gid=0)
- [Guidance & Data Definitions](https://docs.google.com/document/d/1wnm5Cih4qQcIOjZi7pY8cZrz2x_oykUVZf1b291Zr6o)
- [Presentation Deck](https://docs.google.com/presentation/d/1YRoZPvpZZ2Bt1qwf1rLoegYDZ_RdpOHU-12oMPpkmpg)

## Code Conventions

- Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Branch naming: `feature/`, `fix/`, `docs/` prefixes with short descriptions
- Python: follow PEP 8, use type hints
- TypeScript/JavaScript: follow Airbnb style guide
- Keep PRs focused and small when possible

## Build & Test Commands

```bash
# Phase 1: Data pulls (standalone scripts)
pip install -r scripts/requirements.txt
python scripts/pull_gong.py
python scripts/pull_salesforce.py
python scripts/pull_jira_cfr.py
python scripts/pull_slack.py
python scripts/pull_qualtrics.py
python scripts/synthesize.py          # Claude synthesis → data/output/insights.csv

# Phase 2+: Full app
make up                               # docker-compose up (Postgres + backend + frontend)
make migrate                          # alembic upgrade head
make seed                             # load data/output/insights.json into Postgres
make backend-dev                      # uvicorn on port 8000
make frontend-dev                     # vite dev server on port 5173
make test                             # run all tests
```
