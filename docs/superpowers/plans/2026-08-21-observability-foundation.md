# Carveo Observability Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an idle Crawl4AI service, scheduled health monitoring, Prometheus metrics, provisioned Grafana dashboards, and database/queue exporters before live ingestion begins.

**Architecture:** Docker health checks remain the container-readiness authority, a Python APScheduler Beat process performs periodic end-to-end probes, and Prometheus independently scrapes application and infrastructure metrics. Crawl4AI is authenticated, localhost-bound for diagnostics, and unused by ingestion code in this milestone.

**Tech Stack:** Docker Compose, Crawl4AI 0.9.2, Dramatiq 2.2, APScheduler 3, prometheus-client, Prometheus 3.13, Blackbox Exporter, PostgreSQL Exporter, Redis Exporter, Grafana 13.

**Spec:** Approved design in the 2026-08-21 Codex task and `codex.md` operational boundaries.

## Global Constraints

- Keep the frontend in `frontend/` and all operational infrastructure in `backend/`.
- Do not implement a crawler adapter, submit a crawl request, or enable a live source.
- Keep Crawl4AI authenticated and bind host diagnostics to `127.0.0.1`.
- Preserve `/health` as liveness and `/ready` as dependency-backed readiness.
- Store no production credential in Git; defaults are development-only and production overrides remain environment-backed.
- Keep structured JSON logs and bounded Docker log rotation on every service.
- Refresh Graphify after the final repository edit.

---

### Task 1: Health And Metrics Contracts

**Files:**
- Modify: `backend/apps/api/tests/test_api.py`
- Modify: `backend/workers/ingestion/tests/test_worker.py`
- Create: `backend/workers/ingestion/tests/test_monitoring.py`

**Interfaces:**
- Produces: `GET /metrics`, `HealthMonitor.run_cycle()`, worker heartbeat actor, and Beat freshness validation.

- [ ] Add a failing API assertion that `/metrics` returns Prometheus text without appearing in OpenAPI.
- [ ] Add failing worker tests proving heartbeat messages use the operations queue.
- [ ] Add failing monitor tests proving target failures become metrics instead of crashing the cycle.
- [ ] Add failing freshness tests for missing, stale, and current Beat heartbeat values.
- [ ] Run focused tests and confirm they fail because the new interfaces do not exist.

### Task 2: Application Observability

**Files:**
- Modify: `backend/apps/api/pyproject.toml`
- Modify: `backend/apps/api/src/carveo_api/main.py`
- Modify: `backend/workers/ingestion/pyproject.toml`
- Modify: `backend/workers/ingestion/src/carveo_worker/broker.py`
- Modify: `backend/workers/ingestion/src/carveo_worker/tasks.py`
- Create: `backend/workers/ingestion/src/carveo_worker/logging.py`
- Create: `backend/workers/ingestion/src/carveo_worker/monitoring.py`
- Create: `backend/workers/ingestion/src/carveo_worker/beat.py`
- Create: `backend/workers/ingestion/src/carveo_worker/beat_health.py`

**Interfaces:**
- Produces: API metrics at `/metrics`, worker metrics at `:9191/metrics`, Beat metrics at `:9108/metrics`, Redis keys `carveo:worker:last_heartbeat` and `carveo:beat:last_tick`.

- [ ] Add `prometheus-fastapi-instrumentator` and instrument FastAPI with the `carveo_api` namespace.
- [ ] Add Dramatiq's Prometheus extra and middleware on port `9191`.
- [ ] Add APScheduler, HTTPX, and prometheus-client to the worker package.
- [ ] Implement a JSON-safe worker heartbeat actor that records a timestamp in Redis.
- [ ] Implement direct HTTP, Redis, PostgreSQL, and worker-heartbeat probes with labelled Prometheus gauges and histograms.
- [ ] Implement Beat with one non-overlapping, coalesced interval job and an initial immediate cycle.
- [ ] Implement a Beat Docker health command that rejects missing or stale ticks.
- [ ] Run focused tests until green, then run the complete backend suite.

### Task 3: Compose And Prometheus Infrastructure

**Files:**
- Modify: `backend/docker-compose.yml`
- Modify: `backend/.env.example`
- Create: `backend/infra/observability/prometheus/prometheus.yml`
- Create: `backend/infra/observability/prometheus/alerts.yml`
- Create: `backend/infra/observability/blackbox/blackbox.yml`

**Interfaces:**
- Produces: `crawl4ai:11235`, `beat:9108`, `prometheus:9090`, `blackbox-exporter:9115`, `postgres-exporter:9187`, and `redis-exporter:9121` on the Compose network.

- [ ] Add pinned Crawl4AI with hardened runtime settings, token-backed internal access, health check, and localhost diagnostic port.
- [ ] Add Beat from the worker image with dependency URLs and scheduler health check.
- [ ] Add pinned database, Redis, and blackbox exporters without unnecessary host ports.
- [ ] Add pinned Prometheus with persistent storage, runtime token-file rendering, target scrapes, and alert rules.
- [ ] Add Docker health checks, restart policies, resource boundaries, and existing JSON log rotation to every service.
- [ ] Validate Compose interpolation and Prometheus configuration.

### Task 4: Grafana Provisioning

**Files:**
- Create: `backend/infra/observability/grafana/provisioning/datasources/prometheus.yml`
- Create: `backend/infra/observability/grafana/provisioning/dashboards/default.yml`
- Create: `backend/infra/observability/grafana/dashboards/carveo-operations.json`

**Interfaces:**
- Produces: Grafana at `http://localhost:3001`, datasource UID `prometheus`, dashboard UID `carveo-operations`.

- [ ] Provision Prometheus as the default datasource.
- [ ] Provision a version-controlled dashboard provider using polling.
- [ ] Add service status, API traffic, latency, worker, Beat, PostgreSQL, Redis, Crawl4AI, and blackbox panels.
- [ ] Configure a persistent Grafana volume and environment-backed local admin credentials.
- [ ] Validate dashboard JSON and provisioning YAML through the running Grafana API.

### Task 5: Documentation And Live Verification

**Files:**
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `codex.md`

**Interfaces:**
- Produces: reproducible operator commands and documented service URLs.

- [ ] Document the full stack, service URLs, metrics boundaries, credentials, and troubleshooting commands.
- [ ] Run `uv lock` and verify the lockfile.
- [ ] Run backend tests, Ruff, and strict mypy.
- [ ] Run frontend tests and typecheck to detect integration regressions.
- [ ] Run `docker compose config` and Prometheus config validation.
- [ ] Build and start the full stack, then verify every container is healthy.
- [ ] Probe API, web, Crawl4AI, Prometheus, Grafana, Beat metrics, and exporter targets.
- [ ] Verify Prometheus targets and Grafana dashboard provisioning through their APIs.
- [ ] Refresh Graphify and confirm the final repository diff.
