# Carveo

Carveo is a UAE used-car discovery platform with direct catalogue search, transparent market-price positioning, listing details, model intelligence, comparison, and a browser-local buyer workspace.

## Repository

- `frontend/`: Next.js 16 and React 19 application managed exclusively with Bun.
- `backend/apps/api/`: FastAPI request service and Alembic migrations.
- `backend/packages/carveo-core/`: shared catalogue contracts, SQLAlchemy models, repositories, valuation, and fixture seeding.
- `backend/workers/ingestion/`: Redis-backed Dramatiq worker foundation.
- `backend/docker-compose.yml`: integrated PostgreSQL, Redis, API, worker, and web environment.

## Run Everything

Docker Desktop must be running.

```powershell
cd backend
docker compose up --build -d
docker compose ps
```

- Frontend: [http://localhost:3000/en-ae](http://localhost:3000/en-ae)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- API liveness: [http://localhost:8000/health](http://localhost:8000/health)
- Integrated web readiness: [http://localhost:3000/api/ready](http://localhost:3000/api/ready)

Follow operational logs with:

```powershell
cd backend
docker compose logs -f api worker web
```

Stop the stack without deleting database volumes:

```powershell
cd backend
docker compose down
```

## Frontend

The frontend uses FastAPI by default at `http://localhost:8000`. Fixture mode is explicit and reserved for isolated tests.

```powershell
cd frontend
bun install --frozen-lockfile
bun run dev
```

Frontend verification:

```powershell
bun run typecheck
bun run test
bun run test:e2e
bun run test:e2e:api
bun run build
```

## Backend

The Python backend is managed from `backend/` with one `uv.lock`.

```powershell
cd backend
uv run pytest
uv run ruff check .
uv run mypy
uv lock --check
```

Database schema changes belong exclusively to Alembic. The API container upgrades the database and repeatably seeds the approved development fixtures before starting Uvicorn.

## Data Boundary

The running catalogue contains approved development fixture records. Live marketplace crawling remains disabled until a source has documented authorization or licensed access. Missing accident, service, or condition evidence remains unknown.
