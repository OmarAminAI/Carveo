# Carveo Codex Guide

This document is the human-maintained operating guide for developing Carveo with Codex. Graphify is configured separately under `.codex/`, `AGENTS.md`, and `graphify-out/`; generated Graphify data does not belong in this file.

## Product Boundary

Carveo is an English-first UAE used-car discovery platform. It supports direct catalogue search, conversational search refinement, transparent market-price positioning, listing detail, model intelligence, comparison, and a Clerk-authenticated buyer workspace with an anonymous browser fallback.

The current catalogue uses approved development fixtures. Do not introduce live marketplace crawling, copied listing media, or claims of source authorization without a documented legal or commercial approval record. Unknown accident, service, or condition evidence must remain unknown.

## Repository Layout

```text
Carveo/
|-- frontend/                    # Next.js application; the only JavaScript app
|-- backend/
|   |-- apps/api/                # FastAPI HTTP service and Alembic migrations
|   |-- packages/carveo-core/    # Contracts, models, repositories, valuation, fixtures
|   |-- workers/ingestion/       # Redis-backed Dramatiq worker foundation
|   |-- contracts/               # Deterministic OpenAPI contract
|   |-- docker-compose.yml       # Integrated development stack
|   |-- pyproject.toml           # uv workspace and quality configuration
|   `-- uv.lock                  # Reproducible Python dependency lock
|-- .codex/                      # Project-scoped Codex skills, including Graphify
|-- graphify-out/                # Generated Graphify graph and report
|-- AGENTS.md                    # Graphify-generated agent guidance
|-- codex.md                     # This human-maintained project guide
`-- README.md                    # Short operator-facing setup
```

Legacy root-level reference Markdown files are documentation only. Runtime code belongs in `frontend/` or `backend/`.

## Technology Stack

### Frontend

| Area | Technology |
| --- | --- |
| Runtime and package manager | Bun 1.3.x |
| Framework | Next.js 16 App Router |
| UI runtime | React 19 |
| Language | Strict TypeScript |
| Styling | Tailwind CSS v4 |
| Components | shadcn composition on Base UI |
| Authentication | Clerk Next.js SDK with Clerk UI shadcn theme |
| Validation | Zod 4 |
| API client | `openapi-fetch` with generated OpenAPI types |
| Tables | TanStack Table |
| Charts | Recharts 3 |
| Motion | Motion, with reduced-motion support |
| Icons | Lucide React |
| Unit/component tests | Vitest and Testing Library |
| Browser tests | Playwright and axe-core |

Bun is the only supported JavaScript package manager and command runner. Do not add npm, pnpm, Yarn, Vite, or another JavaScript application framework.

### Backend

| Area | Technology |
| --- | --- |
| Runtime | Python 3.12 |
| Workspace/package manager | uv with one lockfile |
| HTTP API | FastAPI 0.141.x and Uvicorn |
| Contracts/settings | Pydantic v2 and Pydantic Settings |
| Persistence | PostgreSQL 18 |
| ORM/database driver | SQLAlchemy 2 async and Psycopg 3 |
| Migrations | Alembic |
| Search | PostgreSQL full-text search and `pg_trgm` |
| Queue | Redis 8 and Dramatiq 2.2 |
| Logging | Structured JSON logs and request IDs |
| Quality | Pytest, Ruff, strict mypy, Testcontainers |
| Orchestration | Docker Compose |

Alembic exclusively owns the production schema. Application startup must never call `metadata.create_all()`.

## Runtime Architecture

Docker Compose in `backend/` is the integrated runtime authority:

| Service | Responsibility | Host port | Readiness dependency |
| --- | --- | --- | --- |
| `postgres` | Catalogue persistence | Internal only | `pg_isready` |
| `redis` | Dramatiq broker | Internal only | `redis-cli ping` |
| `api` | FastAPI catalogue service | `8000` | PostgreSQL `SELECT 1` through `/ready` |
| `worker` | Dramatiq ingestion and operations queues | Internal only | Redis broker health probe |
| `beat` | APScheduler health monitor and worker heartbeat | Internal only | Fresh Redis Beat timestamp |
| `crawl4ai` | Authenticated idle crawler server | `11235` on localhost | Native `/health` probe |
| `prometheus` | Metrics scraping, storage, and alert rules | `9090` on localhost | Native `/-/ready` probe |
| `grafana` | Provisioned operations dashboard | `3001` on localhost | Native `/api/health` probe |
| `blackbox-exporter` | Independent HTTP target probes | Internal only | Exporter binary check |
| `postgres-exporter` | PostgreSQL operational metrics | Internal only | Exporter binary check |
| `redis-exporter` | Redis operational metrics | Internal only | Exporter binary check |
| `web` | Next.js marketplace | `3000` | API readiness through `/api/ready` |

All containers use bounded JSON-file log rotation. The API container migrates and seeds the approved fixture catalogue before Uvicorn starts. Beat probes all runtime dependencies every 30 seconds, while Prometheus independently scrapes application metrics, exporters, and Blackbox HTTP probes.

The frontend consumes a `CatalogueRepository` contract. Integrated development selects the API implementation; isolated frontend tests can select the fixture implementation. Keep both implementations domain-compatible.

## Frontend Routes

| Route | Purpose |
| --- | --- |
| `/en-ae` | UAE discovery home |
| `/en-ae/cars` | URL-filtered catalogue results |
| `/en-ae/cars/[listingId]` | Listing detail and related inventory |
| `/en-ae/find` | Deterministic conversational search workspace |
| `/en-ae/market/[make]/[model]` | Model market intelligence |
| `/en-ae/compare` | Two-to-four vehicle comparison |
| `/en-ae/shortlist` | Anonymous or Clerk-synchronized buyer workspace |
| `/sign-in/[[...sign-in]]` | Clerk sign-in flow |
| `/sign-up/[[...sign-up]]` | Clerk account creation flow |
| `/api/ready` | Web-to-API integrated readiness proxy |

URL search parameters are the source of truth for catalogue filters and sorting. Signed-out shortlist, comparison, saved-search drafts, and conversations remain in the versioned browser profile and merge once after sign-in. Signed-in ownership lives in PostgreSQL; recent views remain browser-local.

## Public API

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Process liveness without external checks |
| `GET /ready` | Database-backed readiness |
| `GET /api/v1/markets` | Supported market metadata |
| `GET /api/v1/listings` | Filtered, sorted, paginated catalogue |
| `GET /api/v1/listings/{listingId}` | Listing detail |
| `GET /api/v1/listings/{listingId}/related` | Related listings |
| `POST /api/v1/compare` | Ordered comparison lookup for one to four IDs |
| `GET /api/v1/models/{make}/{model}/insights` | Model pricing and inventory summary |

Public JSON uses camelCase aliases compatible with the frontend domain. Errors use sanitized RFC 9457-style problem responses. Never expose stack traces, SQL, credentials, or internal connection details.

## Protected Buyer API

All routes below require a Clerk bearer token verified by FastAPI. The verified Clerk `sub` is the only buyer identity input; request bodies and query parameters never select an owner.

| Method and path | Purpose |
| --- | --- |
| `GET /api/v1/me/workspace` | Authoritative shortlist, comparison, saved searches, conversations, and merge state |
| `POST /api/v1/me/workspace/merge` | Idempotent first-sign-in merge of anonymous browser data |
| `PUT/DELETE /api/v1/me/shortlist/{listingId}` | Idempotent shortlist mutation |
| `PUT /api/v1/me/comparison` | Atomic ordered replacement of zero to four listings |
| `GET/POST /api/v1/me/saved-searches` | List or upsert owned searches |
| `DELETE /api/v1/me/saved-searches/{savedSearchId}` | Delete an owned saved search |
| `GET/POST /api/v1/me/conversations` | List or create owned AI conversations |
| `GET /api/v1/me/conversations/{conversationId}` | Read one owned conversation and ordered turns |
| `POST /api/v1/me/conversations/{conversationId}/turns` | Append an owned conversation turn transactionally |

Buyer profiles are created just in time from the verified Clerk subject. Foreign owned identifiers return 404. Clerk user-deletion webhooks and account erasure orchestration remain deferred; do not claim automatic deletion until that webhook is implemented.

## Contracts and Fixtures

FastAPI OpenAPI is the public contract source of truth:

```powershell
cd backend
uv run python -m carveo_api.export_openapi

cd ..\frontend
bun run contracts:generate
bun run contracts:check
```

Generated TypeScript definitions live at `frontend/src/contracts/api.ts`. Commit backend OpenAPI and generated TypeScript changes together.

The canonical UAE fixture dataset lives at:

```text
backend/packages/carveo-core/src/carveo_core/data/ae-listings.json
```

Backend seeding validates it with Pydantic. The frontend fallback validates compatible records with Zod. Do not create a second independent fixture catalogue.

## Environment Variables

Use local `.env` files or deployment secret stores. Commit only `.env.example` templates.

| Variable | Consumer | Purpose |
| --- | --- | --- |
| `POSTGRES_DB` | Compose/PostgreSQL | Database name |
| `POSTGRES_USER` | Compose/PostgreSQL | Database role |
| `POSTGRES_PASSWORD` | Compose/PostgreSQL | Database password; secret outside local defaults |
| `CARVEO_DATABASE_URL` | API | Async PostgreSQL connection URL |
| `CARVEO_REDIS_URL` | Worker | Redis broker URL |
| `CARVEO_CORS_ORIGINS` | API | JSON array of allowed browser origins |
| `CARVEO_CATALOGUE_SOURCE` | Web | `api` for integration or `fixture` for isolated tests |
| `CARVEO_API_INTERNAL_URL` | Web server | Container/internal API base URL |
| `NEXT_PUBLIC_CARVEO_API_URL` | Browser | Public API base URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Web/browser | Clerk development or production publishable key |
| `CLERK_SECRET_KEY` | Web server/API | Clerk server credential injected at runtime; never expose through a public variable or image layer |
| `CARVEO_CLERK_SECRET_KEY` | API | Optional API-specific alias for the same Clerk server credential |
| `CARVEO_CLERK_JWT_KEY` | API | Optional pinned Clerk JWT public key for offline verification |
| `CARVEO_CLERK_AUTHORIZED_PARTIES` | API | Explicit JSON array of accepted frontend origins |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | Web/browser | Local sign-in route, `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | Web/browser | Local sign-up route, `/sign-up` |
| `CARVEO_ENVIRONMENT` | API | Development, test, or production mode |
| `CARVEO_LOG_LEVEL` | API/worker/Beat | Structured log threshold |
| `CARVEO_BEAT_INTERVAL_SECONDS` | Beat | Health sweep interval |
| `CARVEO_BEAT_HEARTBEAT_TTL_SECONDS` | Beat | Scheduler freshness deadline |
| `CRAWL4AI_API_TOKEN` | Crawl4AI/Prometheus | Internal crawler authentication; secret outside local defaults |
| `CRAWL4AI_SECRET_KEY` | Crawl4AI | Signing key; use a random value outside local development |
| `CRAWL4AI_REDIS_PASSWORD` | Crawl4AI | Password for Crawl4AI's private in-container Redis process |
| `POSTGRES_EXPORTER_DSN` | PostgreSQL exporter | Metrics-only database connection URL |
| `GRAFANA_ADMIN_USER` | Grafana | Local administrator name |
| `GRAFANA_ADMIN_PASSWORD` | Grafana | Local administrator password; secret outside local defaults |

Production must reject missing secrets and unsafe wildcard CORS. Never expose a database URL, Redis URL, PAT, API key, or private key through a `NEXT_PUBLIC_*` variable.

Clerk routes are public and marketplace browsing remains anonymous. The local
Compose stack reads `frontend/.env.local` only at container runtime; Docker
build contexts must exclude all `.env` files. Use `clerk env pull` for local
development and deployment secret stores for production. Never copy
`CLERK_SECRET_KEY` into a Docker build argument or image layer.

## GitHub Configuration

### Repository identity

| Setting | Value |
| --- | --- |
| GitHub owner/account | `OmarAminAI` |
| Repository | `Carveo` |
| HTTPS remote | `https://github.com/OmarAminAI/Carveo.git` |
| Remote name | `origin` |
| Branch convention | `codex/<short-purpose>` for Codex-created branches |

### Credential policy

No GitHub password, personal access token, OAuth token, SSH private key, recovery code, or Actions secret belongs in this repository or this document.

The configured Git credential helper is Git Credential Manager (`manager`). Authenticate interactively through the browser-backed credential store:

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth status
git config --global credential.helper manager
git remote -v
```

If GitHub CLI is unavailable, the first authenticated `git fetch` or `git push` can invoke Git Credential Manager. Store CI/CD secrets in GitHub repository or environment secrets. Use the automatic Actions `GITHUB_TOKEN` when its scoped permissions are sufficient; use a narrowly scoped replacement only when required.

Never place a token in a remote URL. This is forbidden:

```text
https://TOKEN@github.com/OmarAminAI/Carveo.git
```

For sandboxed Git inspection, repository ownership can require a command-scoped exception instead of changing global trust:

```powershell
git -c safe.directory="C:/Fast Project/Carveo" status
```

Before pushing, verify the destination and staged content:

```powershell
git remote -v
git status --short
git diff --cached --check
git diff --cached
```

## Development Commands

### Complete integrated stack

```powershell
cd backend
docker compose up --build -d
docker compose ps
docker compose logs -f api worker beat crawl4ai prometheus grafana web
```

Open:

- Frontend: `http://localhost:3000/en-ae`
- API documentation: `http://localhost:8000/docs`
- API liveness: `http://localhost:8000/health`
- API readiness: `http://localhost:8000/ready`
- Integrated web readiness: `http://localhost:3000/api/ready`
- Crawl4AI health: `http://localhost:11235/health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

Stop containers without deleting persistent volumes:

```powershell
cd backend
docker compose down
```

Do not add `-v` unless intentionally deleting local PostgreSQL and Redis data.

### Frontend only

```powershell
cd frontend
bun install --frozen-lockfile
bun run dev
```

### Backend only

```powershell
cd backend
uv sync --frozen
uv run alembic -c apps/api/alembic.ini upgrade head
uv run uvicorn carveo_api.main:app --host 0.0.0.0 --port 8000
```

Prefer Docker Compose for integrated development because PostgreSQL and Redis are behavioral dependencies.

## Verification

Run checks appropriate to the changed surface before committing.

### Backend

```powershell
cd backend
uv run pytest
uv run ruff check .
uv run mypy
uv lock --check
```

### Frontend

```powershell
cd frontend
bun run typecheck
bun run test
bun run build
bun run test:e2e
```

With the integrated Compose stack healthy:

```powershell
cd frontend
bun run test:e2e:api
```

### Containers and contracts

```powershell
cd backend
docker compose config
docker compose ps

cd ..\frontend
bun run contracts:check
```

Do not claim completion based on earlier results. Run fresh verification and report any skipped or environment-dependent checks.

## Engineering Rules

- Preserve the frontend/backend ownership boundary.
- Keep Bun as the sole JavaScript package manager.
- Keep marketplace browsing public; require Clerk only when server-backed buyer data is introduced.
- Treat the verified Clerk user ID as the external identity key; never trust a client-supplied user ID without validating the session token server-side.
- Keep the Python backend in the `backend/` uv workspace.
- Prefer repository interfaces and domain contracts over direct fixture imports.
- Preserve URL-backed filtering and browser-local anonymous profile behavior.
- Use integer AED amounts and timezone-aware UTC timestamps.
- Keep listing condition and market-price claims transparent and evidence-based.
- Add Alembic migrations for schema changes; never mutate production schema at app startup.
- Keep logs structured, sanitized, and correlated with request IDs.
- Do not add live crawling before source authorization is documented.
- Do not overwrite or revert unrelated user changes in a dirty worktree.
- Keep generated OpenAPI and TypeScript contracts synchronized.

## Graphify Boundary

Graphify is a separate code-navigation system, not a section embedded in `codex.md`.

Its project files are:

```text
.codex/skills/graphify/           # Project-scoped Codex skill
AGENTS.md                         # Query/update guidance
graphify-out/graph.json           # Machine-readable knowledge graph
graphify-out/graph.html           # Interactive visualization
graphify-out/GRAPH_REPORT.md      # Generated architecture report
```

The current graph is generated locally in code-only mode, so no external LLM key or source upload is required:

```powershell
graphify . --code-only
graphify cluster-only . --no-label
```

Use scoped graph queries before broad source searches:

```powershell
graphify query "catalogue repository API flow"
graphify explain "SqlAlchemyCatalogueRepository"
graphify path "ApiCatalogueRepository" "create_app()"
```

Graphify refresh is mandatory after every repository change, including code,
documentation, configuration, migrations, dependencies, fixtures, generated
contracts, and agent instructions. Run it after the final edit and before
reporting the task complete:

```powershell
graphify update .
```

Confirm that the command exits successfully and that
`graphify-out/GRAPH_REPORT.md` reports the current Git commit. If Graphify
cannot classify a changed non-code file in code-only mode, the successful
refresh still records the scan; maintain that policy or regenerate the full
semantic graph when an approved API-backed extraction environment is
available. Never silently skip the refresh. If it fails, report the failure
and leave Graphify freshness as an explicit outstanding item.

Do not copy generated graph reports into this guide. Update `codex.md` manually when project policy, stack, commands, or architecture contracts change.

## Current Delivery Boundary

Implemented foundation:

- UAE marketplace frontend routes
- API-backed and fixture-backed frontend repository implementations
- PostgreSQL catalogue persistence and Alembic migration
- FastAPI catalogue endpoints and readiness handling
- OpenAPI-to-TypeScript contract generation
- Redis/Dramatiq worker shell and health probe
- APScheduler Beat with end-to-end service and worker health probes
- Authenticated idle Crawl4AI 0.9.2 container
- Prometheus, Blackbox, PostgreSQL, and Redis exporters
- Provisioned Grafana `Carveo Operations` dashboard
- Docker Compose integration for application, crawler, scheduler, persistence, and observability services
- Clerk frontend authentication, themed sign-in/sign-up routes, and runtime-only Compose secret injection
- FastAPI Clerk bearer-token verification with authorized-party checks
- PostgreSQL-owned shortlist, comparison, saved searches, and AI conversations
- Idempotent anonymous-to-account workspace merge and Clerk-aware frontend synchronization

Intentionally deferred:

- Clerk deletion webhook and automated account-data erasure
- Alerts
- Crawl4AI source adapters and crawl execution
- Unapproved marketplace ingestion
- Object storage
- Dedicated search engine
- Vector database
- Arabic/RTL production content
- Additional GCC markets
