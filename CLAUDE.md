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

## Architecture

The system has three stages:

1. **Data Ingestion & Normalization** — Pull customer signals from Gong, Slack, Jira CFR board,
   Salesforce, and Qualtrics. Normalize into a common schema.
2. **Deduplication & Enrichment** — Deduplicate signals, add metadata (product area, subcategory,
   priority, sentiment, customer context).
3. **Product Backlog Visualization** — Web app for exploring, filtering, and prioritizing the
   consolidated product backlog.

### Key Directories

- `ingestion/` — Data pull and normalization pipelines per source
- `enrichment/` — Deduplication logic, metadata tagging, taxonomy mapping
- `app/` — Product backlog management web application
- `data/` — Schema definitions, sample data, taxonomy references
- `scripts/` — Utility scripts for setup, data loading, etc.

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
# TBD — will be filled in as tech stack is finalized
```
