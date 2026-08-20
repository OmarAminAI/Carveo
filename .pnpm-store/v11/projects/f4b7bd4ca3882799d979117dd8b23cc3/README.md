# Carveo Web

The fixture-powered Carveo buyer experience is a Next.js 16 App Router application using React 19, strict TypeScript, Tailwind CSS v4, Base UI-backed shadcn components, and Bun.

## Run locally

```powershell
cd apps/web
bun install
bun run dev
```

Open [http://localhost:3000/en-ae](http://localhost:3000/en-ae). To use another port, run `bun run dev --port 5176`.

## Verify

```powershell
bun run test
bun run typecheck
bun run build
bun run test:e2e
```

The browser suite starts or reuses the development server at `http://127.0.0.1:5176`. Fixture photographs and their licenses are documented in `public/media/PROVENANCE.md`; no live marketplace data or arbitrary hotlinked media is used.
