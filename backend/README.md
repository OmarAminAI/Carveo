# Carveo Backend

The backend is a Python 3.12 modular monolith with separate Dramatiq worker and APScheduler Beat processes. It owns the public API, PostgreSQL schema, fixture seeding, Redis queue, OpenAPI contract, scheduled health monitoring, operational metrics, structured logs, and Docker Compose environment.

## Services

- `api`: FastAPI request service; runs Alembic and repeatable fixture seeding before Uvicorn.
- `postgres`: PostgreSQL 18 catalogue database with full-text and trigram indexes.
- `redis`: Dramatiq broker and worker health dependency.
- `worker`: queue-connected async ingestion shell; Crawl4AI adapters remain a later milestone.
- `beat`: scheduled end-to-end health probes and worker heartbeat verification.
- `crawl4ai`: authenticated, idle Crawl4AI 0.9.2 server for pre-integration diagnostics.
- `prometheus`: metrics storage, scraping, and health alert evaluation.
- `grafana`: provisioned Prometheus datasource and `Carveo Operations` dashboard.
- `blackbox-exporter`: independent HTTP readiness probes.
- `postgres-exporter`: PostgreSQL operational metrics.
- `redis-exporter`: Redis operational metrics.
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

Crawl4AI health: `http://localhost:11235/health`

Prometheus: `http://localhost:9090`

Grafana: `http://localhost:3001`

The default Grafana development login is `admin` / `carveo-local-grafana`. Set `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, `CRAWL4AI_API_TOKEN`, `CRAWL4AI_SECRET_KEY`, and `CRAWL4AI_REDIS_PASSWORD` in `backend/.env` before using a shared environment. These values are development defaults, not production credentials.

Inspect the operational stack with:

```powershell
docker compose ps
docker compose logs -f beat crawl4ai prometheus grafana
Invoke-RestMethod http://localhost:9090/api/v1/targets
```

Beat runs every 30 seconds by default. It checks the API, web, Crawl4AI, Prometheus, Grafana, PostgreSQL, Redis, and an end-to-end Dramatiq worker heartbeat. A target failure becomes a metric and alert; Beat container health represents scheduler freshness rather than downstream availability.

## Quality

```powershell
cd backend
uv run pytest
uv run ruff check .
uv run mypy
uv lock --check
```

Export OpenAPI with `uv run python -m carveo_api.export_openapi`, then regenerate frontend definitions with `bun run contracts:generate` from `../frontend`.

Validate Prometheus configuration against the pinned image:

```powershell
docker compose run --rm --no-deps --entrypoint /bin/promtool prometheus check config /etc/prometheus/prometheus.yml
```
