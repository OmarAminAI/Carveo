# Authenticated Buyer Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify Clerk sessions in FastAPI and persist each authenticated buyer's shortlist, comparison set, saved searches, and AI conversations in PostgreSQL while retaining anonymous browser-local behavior.

**Architecture:** Public catalogue routes remain unchanged. Protected `/api/v1/me/*` routes resolve a verified Clerk subject, JIT-provision a minimal buyer profile, and delegate all ownership and transaction rules to a dedicated SQLAlchemy repository. The Next.js `ProfileProvider` switches between browser-local anonymous state and token-authenticated server state, performing one idempotent first-sign-in merge.

**Tech Stack:** Python 3.12, FastAPI 0.141, `clerk-backend-api` 6.x, Pydantic v2, SQLAlchemy 2 async, PostgreSQL 18, Alembic, Next.js 16, React 19, Clerk Next.js 7, strict TypeScript, Bun, Vitest, Pytest, HTTPX, Testcontainers.

**Spec:** `docs/superpowers/specs/2026-08-21-buyer-workspace-auth-design.md`

## Global Constraints

- Stay on `codex/buyer-search-refactor-plan`; do not create a worktree.
- Bun remains the only JavaScript package manager and command runner.
- PostgreSQL is the behavioral persistence source of truth; do not substitute SQLite for repository integration tests.
- Alembic exclusively owns schema creation.
- Public catalogue and operational routes remain unauthenticated.
- Never accept a buyer identity from request JSON, query parameters, or custom identity headers.
- Never log Clerk tokens, authorization headers, secret keys, or raw JWT payloads.
- Clerk secrets are runtime-only and excluded from Git and Docker build contexts.
- Protected foreign resources return 404 so ownership is not disclosed.
- Write every behavior test first and observe the expected failure before implementation.
- Regenerate OpenAPI and TypeScript contracts together.
- Run `graphify update .` after the final repository edit.

---

### Task 1: Clerk Request Authentication Boundary

**Files:**
- Create: `backend/apps/api/src/carveo_api/auth.py`
- Create: `backend/apps/api/tests/test_auth.py`
- Modify: `backend/apps/api/src/carveo_api/settings.py`
- Modify: `backend/apps/api/pyproject.toml`
- Modify: `backend/uv.lock`

**Interfaces:**
- Produces: `AuthenticatedBuyer(clerk_user_id: str)`.
- Produces: `RequestAuthenticator.authenticate(request: Request) -> Awaitable[AuthenticatedBuyer]`.
- Produces: `ClerkRequestAuthenticator(secret_key, authorized_parties, jwt_key=None)`.
- Produces: `require_buyer(request: Request) -> AuthenticatedBuyer` dependency factory wiring.

- [ ] **Step 1: Write failing authentication tests**

```python
@pytest.mark.anyio
async def test_missing_token_returns_unauthorized_problem(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.get("/api/v1/me/workspace")
    assert response.status_code == 401
    assert response.json()["type"].endswith("/authentication-required")

@pytest.mark.anyio
async def test_verified_subject_is_returned_without_client_identity() -> None:
    buyer = await FakeAuthenticator("user_clerk_1").authenticate(request)
    assert buyer.clerk_user_id == "user_clerk_1"
```

- [ ] **Step 2: Run the focused tests and confirm they fail because the auth module and route do not exist**

Run: `cd backend && uv run pytest apps/api/tests/test_auth.py -q`

- [ ] **Step 3: Add the official SDK and settings**

Add `clerk-backend-api>=6,<7` to the API package and run `uv lock`. Add settings for the secret key, optional JWT key, and explicit authorized parties. Production validation must reject an empty authorized-party list and reject configurations with neither secret nor JWT key.

- [ ] **Step 4: Implement the authentication interface**

Use one reusable Clerk SDK client. Run synchronous SDK verification off the event loop with `anyio.to_thread.run_sync`. Pass `AuthenticateRequestOptions(authorized_parties=..., jwt_key=...)`, require `is_signed_in`, and extract only a non-empty string `sub`. Convert all expected verification failures into one internal `AuthenticationError` without exposing Clerk's reason.

- [ ] **Step 5: Add RFC 9457 authentication mapping and test injection**

Allow `create_app(authenticator=FakeAuthenticator(...))`. Missing or invalid authentication returns the same sanitized 401 shape. Unexpected SDK/JWKS failures return a sanitized 503 `authentication-unavailable` problem and do not affect `/ready`.

- [ ] **Step 6: Run focused and quality checks**

Run:

```powershell
cd backend
uv run pytest apps/api/tests/test_auth.py -q
uv run ruff check apps/api/src/carveo_api/auth.py apps/api/tests/test_auth.py
uv run mypy
uv lock --check
```

- [ ] **Step 7: Commit the authentication boundary**

```powershell
git add backend/apps/api backend/uv.lock
git commit -m "feat: verify Clerk sessions in FastAPI"
```

---

### Task 2: Buyer Contracts, Tables, and Migration

**Files:**
- Create: `backend/packages/carveo-core/src/carveo_core/buyer_contracts.py`
- Modify: `backend/packages/carveo-core/src/carveo_core/models.py`
- Create: `backend/apps/api/alembic/versions/20260821_0002_buyer_workspace.py`
- Modify: `backend/packages/carveo-core/tests/test_models.py`
- Modify: `backend/apps/api/tests/test_migrations.py`

**Interfaces:**
- Produces: `BuyerWorkspace`, `SavedSearch`, `ConversationSummary`, `Conversation`, `ConversationTurn`, `AnonymousWorkspaceMergeRequest`, `WorkspaceMergeResponse`, `ComparisonUpdate`, `SavedSearchUpsert`, `ConversationCreate`, and `ConversationTurnCreate` Pydantic contracts.
- Produces SQLAlchemy models: `BuyerProfileRecord`, `BuyerShortlistItemRecord`, `BuyerComparisonItemRecord`, `BuyerSavedSearchRecord`, `BuyerConversationRecord`, and `BuyerConversationTurnRecord`.

- [ ] **Step 1: Write failing model and migration assertions**

Assert unique Clerk identity, shortlist pair uniqueness, comparison position uniqueness, saved-query uniqueness, conversation client-ID uniqueness, turn sequence uniqueness, all foreign keys, and expected indexes after Alembic upgrades an empty PostgreSQL database.

- [ ] **Step 2: Run the tests and confirm the new tables are absent**

Run: `cd backend && uv run pytest packages/carveo-core/tests/test_models.py apps/api/tests/test_migrations.py -q`

- [ ] **Step 3: Define strict camelCase contracts**

Use bounded fields: listing IDs at 160 characters, saved labels at 120, query strings at 2,000, conversation titles at 160, client IDs at 100, and turn content at 8,000. Enforce unique comparison IDs and a maximum of four in `ComparisonUpdate`.

- [ ] **Step 4: Define relational models and constraints**

Use PostgreSQL UUID keys, UTC timestamps, JSONB only for interpreted intent, cascade deletion from buyer profiles and conversations, and check constraints for comparison positions, conversation status, turn role, and non-negative turn sequence.

- [ ] **Step 5: Write upgrade and downgrade migration `20260821_0002`**

Create tables in parent-first order and indexes on Clerk ID, profile foreign keys, saved-search freshness, conversation freshness, and conversation sequence. Downgrade in exact reverse dependency order.

- [ ] **Step 6: Verify migrations and models**

Run:

```powershell
cd backend
uv run pytest packages/carveo-core/tests/test_models.py apps/api/tests/test_migrations.py -q
uv run alembic -c apps/api/alembic.ini upgrade head
uv run alembic -c apps/api/alembic.ini current
```

- [ ] **Step 7: Commit contracts and schema**

```powershell
git add backend/packages/carveo-core backend/apps/api/alembic
git commit -m "feat: add buyer workspace schema"
```

---

### Task 3: SQLAlchemy Buyer Workspace Repository

**Files:**
- Create: `backend/packages/carveo-core/src/carveo_core/buyer.py`
- Create: `backend/packages/carveo-core/src/carveo_core/buyer_sql_repository.py`
- Create: `backend/packages/carveo-core/tests/test_buyer_repository.py`

**Interfaces:**
- Produces protocol methods:

```python
class BuyerWorkspaceRepository(Protocol):
    async def get_workspace(self, clerk_user_id: str) -> BuyerWorkspace: ...
    async def merge_anonymous(self, clerk_user_id: str, payload: AnonymousWorkspaceMergeRequest) -> WorkspaceMergeResponse: ...
    async def add_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace: ...
    async def remove_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace: ...
    async def replace_comparison(self, clerk_user_id: str, listing_public_ids: list[str]) -> BuyerWorkspace: ...
    async def upsert_saved_search(self, clerk_user_id: str, payload: SavedSearchUpsert) -> SavedSearch: ...
    async def delete_saved_search(self, clerk_user_id: str, saved_search_id: UUID) -> bool: ...
    async def list_conversations(self, clerk_user_id: str) -> list[ConversationSummary]: ...
    async def create_conversation(self, clerk_user_id: str, payload: ConversationCreate) -> Conversation: ...
    async def get_conversation(self, clerk_user_id: str, conversation_id: UUID) -> Conversation | None: ...
    async def append_turn(self, clerk_user_id: str, conversation_id: UUID, payload: ConversationTurnCreate) -> Conversation | None: ...
```

- [ ] **Step 1: Write PostgreSQL integration tests first**

Cover JIT profile creation, cross-user isolation, idempotent shortlist operations, comparison order and replacement, twelve-search cap and query deduplication, conversation sequence ordering, hidden foreign resources, invalid listing IDs, and one-time merge behavior.

- [ ] **Step 2: Run focused tests and confirm repository imports fail**

Run: `cd backend && uv run pytest packages/carveo-core/tests/test_buyer_repository.py -q -m integration`

- [ ] **Step 3: Implement mapping and profile locking helpers**

Create `_get_or_create_profile`, `_lock_profile`, `_resolve_listings`, and `_to_workspace` helpers. Use `INSERT ... ON CONFLICT` where it improves idempotency and `SELECT ... FOR UPDATE` for the one-time merge and ordered comparison replacement.

- [ ] **Step 4: Implement shortlist, comparison, and saved-search transactions**

Resolve only listing public IDs. Comparison replacement validates all IDs before deleting the prior set. Saved-search upsert deduplicates by canonical query and removes the oldest record only when inserting a thirteenth unique search.

- [ ] **Step 5: Implement conversation ownership and sequencing**

Create by `(profile_id, client_id)`. Append turns while locking the conversation and assign `max(sequence)+1` inside the transaction. Ownership predicates must be present in every lookup.

- [ ] **Step 6: Implement the idempotent merge**

Lock the profile row, return `merged=False` when already stamped, apply the four deterministic merge rules, stamp `anonymous_merged_at`, commit once, and return unknown listing public IDs in `ignored_listing_ids`.

- [ ] **Step 7: Run repository and quality verification**

Run:

```powershell
cd backend
uv run pytest packages/carveo-core/tests/test_buyer_repository.py -q -m integration
uv run ruff check packages/carveo-core
uv run mypy
```

- [ ] **Step 8: Commit the repository**

```powershell
git add backend/packages/carveo-core
git commit -m "feat: persist buyer-owned workspace data"
```

---

### Task 4: Protected FastAPI Buyer Routes

**Files:**
- Create: `backend/apps/api/src/carveo_api/buyer_routes.py`
- Create: `backend/apps/api/tests/test_buyer_api.py`
- Modify: `backend/apps/api/src/carveo_api/main.py`
- Modify: `backend/apps/api/src/carveo_api/problems.py`

**Interfaces:**
- Consumes: verified `AuthenticatedBuyer` and `BuyerWorkspaceRepository`.
- Produces: the complete `/api/v1/me/*` contract from the design spec.

- [ ] **Step 1: Write failing API contract tests**

Test every route, bearer-token requirement, camelCase serialization, merge response, comparison validation, saved-search upsert/deletion, conversation creation/turn append, 404 ownership hiding, and sanitized repository failures.

- [ ] **Step 2: Run focused tests and confirm routes return 404**

Run: `cd backend && uv run pytest apps/api/tests/test_buyer_api.py -q`

- [ ] **Step 3: Add buyer repository dependency wiring**

`create_app` accepts optional catalogue repository, buyer repository, authenticator, and readiness check. Production creates both SQL repositories from the same request-scoped `AsyncSession`.

- [ ] **Step 4: Implement the protected router**

Use one authentication dependency for the router. Keep route handlers thin and map domain `UnknownListingError`, `OwnedResourceNotFound`, and validation failures to existing problem helpers.

- [ ] **Step 5: Expand CORS safely**

Allow `Authorization`, `Content-Type`, and `X-Request-ID`. Keep explicit origins and `allow_credentials=False` because bearer tokens are used cross-origin.

- [ ] **Step 6: Verify public routes remain public**

Run:

```powershell
cd backend
uv run pytest apps/api/tests/test_api.py apps/api/tests/test_auth.py apps/api/tests/test_buyer_api.py -q
uv run ruff check apps/api
uv run mypy
```

- [ ] **Step 7: Commit protected routes**

```powershell
git add backend/apps/api
git commit -m "feat: expose authenticated buyer workspace API"
```

---

### Task 5: OpenAPI and TypeScript Buyer Contracts

**Files:**
- Modify: `backend/contracts/openapi.json`
- Modify: `frontend/src/contracts/api.ts`
- Modify: `backend/apps/api/tests/test_contract.py`
- Modify: `frontend/src/domain/schemas.ts`

**Interfaces:**
- Produces: generated path and schema types for all `/api/v1/me/*` routes.
- Produces frontend Zod schemas and types matching API camelCase responses.

- [ ] **Step 1: Add failing deterministic contract assertions**

Assert protected paths, bearer auth scheme, request bodies, and response component names exist in exported OpenAPI.

- [ ] **Step 2: Export OpenAPI and regenerate TypeScript**

Run:

```powershell
cd backend
uv run python -m carveo_api.export_openapi
cd ..\frontend
bun run contracts:generate
```

- [ ] **Step 3: Add matching frontend Zod schemas**

Define `savedSearchSchema`, `conversationTurnSchema`, `conversationSummarySchema`, `conversationSchema`, `buyerWorkspaceSchema`, and `workspaceMergeResponseSchema`. Upgrade `BrowserProfile` to version 2 with anonymous conversations and a migration from version 1.

- [ ] **Step 4: Verify contract determinism and frontend types**

Run:

```powershell
cd backend
uv run pytest apps/api/tests/test_contract.py -q
cd ..\frontend
bun run contracts:check
bun run typecheck
```

- [ ] **Step 5: Commit generated contracts together**

```powershell
git add backend/contracts backend/apps/api/tests/test_contract.py frontend/src/contracts frontend/src/domain
git commit -m "feat: publish buyer workspace contracts"
```

---

### Task 6: Authenticated Frontend Workspace Client

**Files:**
- Create: `frontend/src/profile/buyer-workspace-client.ts`
- Create: `frontend/src/profile/buyer-workspace-client.test.ts`
- Modify: `frontend/src/profile/browser-profile.ts`
- Modify: `frontend/src/profile/browser-profile.test.ts`

**Interfaces:**
- Produces: `BuyerWorkspaceClient(baseUrl, getToken)` with typed methods matching protected API routes.
- Produces: `toAnonymousMergePayload(profile)` and `applyWorkspace(profile, workspace)` pure functions.

- [ ] **Step 1: Write failing token/client tests**

Assert every request includes a current bearer token, 401 triggers exactly one fresh-token retry, non-auth failures throw `WorkspaceRequestError`, and no method accepts a user ID.

- [ ] **Step 2: Write failing profile-v2 migration tests**

Assert version-1 profiles gain an empty conversation list, malformed conversations are removed, comparison remains capped at four, and merge payloads omit recent views.

- [ ] **Step 3: Implement the typed client**

Use generated OpenAPI request/response types where practical and Zod-parse all server responses. Set `Content-Type` only for JSON bodies and never persist the token.

- [ ] **Step 4: Implement pure profile conversion helpers**

Server workspace replaces account-owned arrays. Recent views remain from the current anonymous profile only until sign-in succeeds, then account-derived profile data is held in memory rather than written to local storage.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
cd frontend
bun run test -- src/profile/buyer-workspace-client.test.ts src/profile/browser-profile.test.ts
bun run typecheck
```

- [ ] **Step 6: Commit the frontend client**

```powershell
git add frontend/src/profile frontend/src/domain/schemas.ts
git commit -m "feat: add authenticated buyer workspace client"
```

---

### Task 7: Clerk-Aware Profile Provider and Conversation Persistence

**Files:**
- Modify: `frontend/src/profile/profile-provider.tsx`
- Modify: `frontend/src/profile/profile-provider.test.tsx`
- Modify: `frontend/src/components/save-search-button.tsx`
- Modify: `frontend/src/components/shortlist-workspace.tsx`
- Modify: `frontend/src/components/comparison-workspace.tsx`
- Modify: `frontend/src/components/assistant-workspace.tsx`
- Modify: `frontend/src/components/assistant-workspace.test.tsx`
- Modify: `frontend/src/app/en-ae/shortlist/page.tsx`

**Interfaces:**
- `ProfileProvider` consumes Clerk `useAuth()` and `useUser()` only through a small internal adapter.
- Context adds `mode: "loading" | "anonymous" | "authenticated" | "error"`, `retrySync()`, and conversation create/append methods while preserving existing action names.

- [ ] **Step 1: Write failing provider transition tests**

Mock Clerk at the SDK boundary. Cover anonymous local persistence, one merge after sign-in, authoritative server hydration, no account-data localStorage writes, optimistic mutation rollback, one retry command, and fresh anonymous state after sign-out.

- [ ] **Step 2: Run provider tests and confirm new modes are absent**

Run: `cd frontend && bun run test -- src/profile/profile-provider.test.tsx`

- [ ] **Step 3: Implement the state machine**

Hydrate local state once. When Clerk becomes signed in, create one client, merge once per user transition, and ignore stale async results through an effect generation counter. When signed out after authentication, remove the storage key before creating and persisting a fresh anonymous profile.

- [ ] **Step 4: Implement optimistic mutations with scoped rollback**

Apply shortlist, comparison, and saved-search changes immediately. On failure, restore only the affected confirmed slice, set a recoverable error message, and preserve unrelated successful mutations.

- [ ] **Step 5: Persist deterministic conversations**

Anonymous assistant messages update the local version-2 conversation record. Authenticated messages create a server conversation by client ID and append buyer/assistant turns in order. `Start over` archives the current local view and starts a new client ID without deleting history.

- [ ] **Step 6: Update buyer-workspace copy and states**

Replace “Stored only in this browser” with mode-aware copy. Show a compact synchronization failure with a Retry command. Do not add disabled account, alert, or notification controls.

- [ ] **Step 7: Run component and frontend suites**

Run:

```powershell
cd frontend
bun run test
bun run typecheck
bun run build
```

- [ ] **Step 8: Commit frontend integration**

```powershell
git add frontend/src/profile frontend/src/components frontend/src/app/en-ae/shortlist
git commit -m "feat: sync buyer workspace through Clerk"
```

---

### Task 8: Runtime Configuration, Integrated Verification, and Documentation

**Files:**
- Modify: `.dockerignore`
- Modify: `backend/.env.example`
- Modify: `frontend/.env.example`
- Modify: `backend/docker-compose.yml`
- Modify: `codex.md`
- Modify: `frontend/e2e/buyer-journeys.spec.ts`

**Interfaces:**
- API container receives Clerk credentials only at runtime.
- Web and API share explicit authorized localhost origin configuration.

- [ ] **Step 1: Add an API-enabled browser journey**

Test sign-in-independent public browsing remains usable and add a test-auth fixture journey for authenticated merge, shortlist persistence after reload, comparison persistence, saved search reopening, and conversation restoration. Never use a real Clerk credential in CI fixtures.

- [ ] **Step 2: Configure runtime-only Clerk environment**

Add the ignored local Clerk env file to the API service using optional Compose `env_file` syntax. Add `CARVEO_CLERK_AUTHORIZED_PARTIES=["http://localhost:3000"]`. Keep all `.env` patterns excluded from Docker context and provide placeholders only in examples.

- [ ] **Step 3: Update the operator guide**

Document protected routes, JIT buyer profiles, runtime secret flow, anonymous merge semantics, and the deferred deletion webhook. Remove statements that the buyer workspace is always browser-local.

- [ ] **Step 4: Run complete backend verification**

Run:

```powershell
cd backend
uv run pytest
uv run ruff check .
uv run mypy
uv lock --check
uv run alembic -c apps/api/alembic.ini upgrade head
```

- [ ] **Step 5: Run complete frontend and contract verification**

Run:

```powershell
cd frontend
bun run contracts:check
bun run typecheck
bun run test
bun run build
bun run test:e2e:api
```

- [ ] **Step 6: Rebuild and probe the integrated stack**

Run:

```powershell
cd backend
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

Verify all twelve services are healthy. Probe `/health`, `/ready`, public catalogue routes, a protected 401 response without a token, and authenticated workspace behavior with a real browser session. Confirm Docker image history and build context contain no `.env.local` or Clerk secret.

- [ ] **Step 7: Refresh Graphify and inspect the final diff**

Run:

```powershell
cd ..
graphify update .
git diff --check
git status --short
```

- [ ] **Step 8: Commit operations and documentation**

```powershell
git add .dockerignore backend/.env.example backend/docker-compose.yml frontend/.env.example frontend/e2e codex.md graphify-out
git commit -m "chore: integrate authenticated workspace runtime"
```
