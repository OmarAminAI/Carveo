# Carveo Context Map

Carveo uses a multi-context domain-document layout. Read the context documents relevant to the work before changing domain behavior or terminology.

| Context | Domain document | Context decisions |
| --- | --- | --- |
| Buyer experience | `frontend/CONTEXT.md` | `frontend/docs/adr/` |
| Catalogue and buyer data | `backend/packages/carveo-core/CONTEXT.md` | `backend/packages/carveo-core/docs/adr/` |
| Ingestion | `backend/workers/ingestion/CONTEXT.md` | `backend/workers/ingestion/docs/adr/` |

System-wide decisions live in `docs/adr/`.

Context documents and decision directories are created lazily when terminology or decisions are resolved. Their absence does not block exploration.
