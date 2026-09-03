# Domain Docs

Carveo uses a multi-context domain-document layout.

Before exploring, read `CONTEXT-MAP.md`, then the `CONTEXT.md` and ADRs
for every relevant context. Also inspect `docs/adr/` for system-wide decisions.

Planned contexts:

- Buyer experience: `frontend/CONTEXT.md`
- Catalogue and buyer data: `backend/packages/carveo-core/CONTEXT.md`
- Ingestion: `backend/workers/ingestion/CONTEXT.md`

Context-specific decisions live under each context's `docs/adr/`.
System-wide decisions live under the root `docs/adr/`.

Missing context files should not block work. Domain-modeling workflows create
them lazily when terminology or decisions are resolved.

Use glossary terminology consistently. Explicitly flag proposals that
contradict an existing ADR.
