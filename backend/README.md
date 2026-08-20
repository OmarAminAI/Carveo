# Carveo Backend

The backend is a Python 3.12 modular monolith with a separate Dramatiq worker. It owns the public API, PostgreSQL schema, fixture seeding, Redis queue, OpenAPI contract, operational logging, and Docker Compose environment.

## Services

- `api`: FastAPI request service; runs Alembic and repeatable fixture seeding before Uvicorn.
- `postgres`: PostgreSQL 18 catalogue database with full-text and trigram indexes.
- `redis`: Dramatiq broker and worker health dependency.
- `worker`: queue-connected async ingestion shell; Crawl4AI adapters remain a later milestone.
- `web`: the sibling Bun/Next.js frontend, built from `../frontend`.

## Run

```powershell
cd backend
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Frontend: `http://localhost:3000/en-ae`

API docs: `http://localhost:8000/docs`

Liveness: `http://localhost:8000/health`

Readiness: `http://localhost:8000/ready`

## Quality

```powershell
cd backend
uv run pytest
uv run ruff check .
uv run mypy
uv lock --check
```

Export OpenAPI with `uv run python -m carveo_api.export_openapi`, then regenerate frontend definitions with `bun run contracts:generate` from `../frontend`.
