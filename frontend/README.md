# Carveo Frontend

This is the only JavaScript application in Carveo. It uses Bun for package management and scripts, with Next.js 16 App Router, React 19, strict TypeScript, Tailwind CSS v4, and Base UI-backed shadcn components.

## Run locally

```powershell
cd frontend
bun install
bun run dev
```

Open [http://localhost:3000/en-ae](http://localhost:3000/en-ae). Isolated tests use fixture mode. For integrated development, start `docker compose up --build` from `../backend`, or set `CARVEO_CATALOGUE_SOURCE=api` and `CARVEO_API_INTERNAL_URL=http://localhost:8000` before running the frontend.

## Verify

```powershell
bun run test
bun run typecheck
bun run build
bun run test:e2e
```

The browser suite starts or reuses the development server at `http://127.0.0.1:5176`. Fixture photographs and their licenses are documented in `public/media/PROVENANCE.md`; no live marketplace data or arbitrary hotlinked media is used. The frontend does not use npm, pnpm, Yarn, Vite, or a second JavaScript framework.
