.PHONY: up down backend-install backend-dev seed test

up:
	docker compose up -d

down:
	docker compose down

backend-install:
	cd backend && pip install -e ".[dev]"

backend-dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

seed:
	python scripts/seed_db.py

test:
	cd backend && python -m pytest tests/ -v
