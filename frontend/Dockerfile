FROM oven/bun:1.3.14 AS build
WORKDIR /workspace
COPY frontend/package.json frontend/bun.lock ./frontend/
RUN cd frontend && bun install --frozen-lockfile
COPY frontend frontend
COPY backend/contracts backend/contracts
COPY backend/packages/carveo-core/src/carveo_core/data backend/packages/carveo-core/src/carveo_core/data
WORKDIR /workspace/frontend
RUN bun run build

FROM oven/bun:1.3.14-slim
WORKDIR /workspace/frontend
ENV NODE_ENV=production
COPY --from=build /workspace/frontend ./
EXPOSE 3000
CMD ["bun", "run", "start"]
