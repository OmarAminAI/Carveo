FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY apps/api apps/api
COPY packages/carveo-core packages/carveo-core
COPY workers/ingestion workers/ingestion
RUN uv sync --frozen --no-dev --package carveo-api

EXPOSE 8000
CMD ["sh", "-c", "uv run --frozen --package carveo-api alembic -c apps/api/alembic.ini upgrade head && uv run --frozen --package carveo-api python -m carveo_api.seed && uv run --frozen --package carveo-api uvicorn carveo_api.main:app --host 0.0.0.0 --port 8000"]
