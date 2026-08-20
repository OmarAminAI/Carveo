FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY apps/api apps/api
COPY packages/carveo-core packages/carveo-core
COPY workers/ingestion workers/ingestion
RUN uv sync --frozen --no-dev --package carveo-worker

CMD ["uv", "run", "--frozen", "--package", "carveo-worker", "dramatiq", "carveo_worker.tasks", "--processes", "1", "--threads", "4"]
