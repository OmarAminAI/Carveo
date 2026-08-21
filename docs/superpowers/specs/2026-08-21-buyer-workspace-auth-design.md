# Authenticated Buyer Workspace Design

## Purpose

Add Clerk-authenticated, PostgreSQL-backed ownership for Carveo shortlists,
comparison selections, saved searches, and AI conversations while preserving
public catalogue browsing and anonymous browser-local use.

This design does not store passwords, replace Clerk user management, protect
catalogue reads, or introduce the LangGraph AI pipeline. It establishes the
identity and persistence boundary that those later capabilities can use.

## Architectural Decision

Use the official Clerk Python SDK to authenticate requests at FastAPI and use
normalized PostgreSQL tables for buyer-owned data.

Alternatives rejected:

- A single JSONB buyer-profile row makes independent updates, constraints,
  ordering, and future querying unnecessarily difficult.
- Event sourcing adds replay, projection, and operational complexity without a
  current audit or temporal-query requirement.
- Synchronizing full Clerk user records through webhooks introduces eventual
  consistency for data Carveo does not need. Carveo only needs the verified
  current user's Clerk subject identifier.

## Security Boundary

Catalogue, listing, comparison lookup, market insight, health, readiness, and
metrics behavior remains unchanged. Only routes under `/api/v1/me/` require a
valid Clerk session token.

The frontend sends the short-lived Clerk session token in the `Authorization:
Bearer <token>` header. FastAPI authenticates the complete request using
`clerk-backend-api` and validates:

- JWT signature through Clerk's cached JWKS or an optional configured JWT key.
- Expiration and not-before claims.
- Session-token type and signed-in state.
- The `azp` claim against explicitly configured authorized frontend origins.
- The `sub` claim as a non-empty Clerk user identifier.

FastAPI must never accept a user identifier from request JSON, query strings,
or frontend-controlled headers. Repository methods receive the verified Clerk
subject from the authentication dependency.

Authentication failures return sanitized RFC 9457 problem responses with 401
status. Authorization failures return 403. Logs may include a request ID and a
non-reversible hash of the Clerk subject, but never session tokens, secret keys,
authorization headers, or raw Clerk payloads.

The Clerk secret is runtime-only. It must remain excluded from Git and Docker
build contexts. Production requires a configured secret or JWT key and explicit
authorized parties.

## Identity Model

`buyer_profiles` stores only Carveo's internal UUID, a unique indexed
`clerk_user_id`, merge state, and timestamps. It does not duplicate the buyer's
email address, name, avatar, password, or Clerk metadata.

The profile is provisioned synchronously on the first valid authenticated
workspace request. This avoids a webhook race during first sign-in. Clerk
remains the identity source of truth; PostgreSQL owns only Carveo application
data.

Account-deletion synchronization is deferred until production webhook
configuration is approved. A later idempotent `user.deleted` webhook can soft
delete or purge the profile without changing the ownership model.

## Persistence Model

### `buyer_profiles`

- UUID primary key.
- Unique, indexed Clerk user ID.
- Nullable `anonymous_merged_at` timestamp.
- Created and updated UTC timestamps.

### `buyer_shortlist_items`

- Profile UUID and listing UUID foreign keys.
- Unique profile/listing pair.
- Created UTC timestamp for stable ordering.
- Cascade deletion when the buyer profile is removed.

### `buyer_comparison_items`

- Profile UUID and listing UUID foreign keys.
- Position constrained to zero through three.
- Unique profile/listing and profile/position pairs.
- Replaced transactionally as one ordered comparison set.

### `buyer_saved_searches`

- UUID primary key and profile UUID foreign key.
- Buyer-visible label and canonical URL query string.
- Unique profile/query pair for deterministic deduplication.
- Created and updated UTC timestamps.
- Maximum twelve active saved searches per profile.

### `buyer_conversations`

- UUID primary key, profile UUID foreign key, and unique browser-generated
  client ID within the profile.
- Buyer-visible title, `active` or `archived` status, and JSONB interpreted
  search intent.
- Created and updated UTC timestamps.

### `buyer_conversation_turns`

- UUID primary key and conversation UUID foreign key.
- Monotonic sequence number unique within a conversation.
- Role constrained to `buyer` or `assistant`.
- Plain-text content with a bounded length.
- Created UTC timestamp.

Listing references use the internal listing UUID. Public API responses expose
only listing public IDs. Foreign keys preserve referential integrity while the
catalogue's existing lifecycle state retains removed listings for its configured
history window.

## API Contract

All protected responses use the existing camelCase alias convention.

### Workspace

- `GET /api/v1/me/workspace` returns shortlist IDs, ordered comparison IDs,
  saved searches, conversation summaries, and merge state.
- `POST /api/v1/me/workspace/merge` accepts the anonymous browser payload and
  returns the authoritative workspace plus `merged: true|false`.

The merge endpoint is idempotent. It executes only while
`anonymous_merged_at` is null. Concurrent attempts serialize on the buyer
profile row; exactly one marks the merge complete.

Merge rules:

- Shortlist: additive union of valid listing IDs.
- Comparison: preserve server order, append anonymous IDs, deduplicate, and
  keep the first four valid IDs.
- Saved searches: deduplicate by canonical query; server records win label and
  timestamp conflicts.
- Conversations: deduplicate by client ID; existing server conversations win.
- Invalid or unknown listing IDs are reported in `ignoredListingIds` and never
  break the whole merge.

### Shortlist

- `PUT /api/v1/me/shortlist/{listingId}` is an idempotent add.
- `DELETE /api/v1/me/shortlist/{listingId}` is an idempotent removal.

An unknown listing returns a sanitized 404 problem.

### Comparison

- `PUT /api/v1/me/comparison` replaces the ordered set with zero to four unique
  valid listing IDs in one transaction.

Duplicate IDs or more than four IDs return a validation problem. Unknown IDs
are rejected so the client cannot persist a partly misleading comparison.

### Saved Searches

- `GET /api/v1/me/saved-searches` lists newest first.
- `POST /api/v1/me/saved-searches` creates or updates by canonical query.
- `DELETE /api/v1/me/saved-searches/{savedSearchId}` removes only an owned row.

The API validates label length and parses the query as a bounded query string.
It stores no arbitrary executable expression or external URL.

### Conversations

- `GET /api/v1/me/conversations` returns summaries newest first.
- `POST /api/v1/me/conversations` creates or returns a conversation by client
  ID and may include initial turns.
- `GET /api/v1/me/conversations/{conversationId}` returns one owned
  conversation and its ordered turns.
- `POST /api/v1/me/conversations/{conversationId}/turns` appends the next turn
  transactionally.

Access to another buyer's resource returns 404, not 403, to avoid confirming
that the identifier exists.

## Repository Boundary

Add a `BuyerWorkspaceRepository` protocol to `carveo-core` and a SQLAlchemy
implementation that owns transactions, ordering, limits, deduplication, and
ownership predicates. FastAPI routes perform authentication, request/response
mapping, and problem translation only.

The authentication dependency is an interface. Production uses
`ClerkRequestAuthenticator`; tests inject a deterministic authenticator and
never call Clerk or the network.

## Frontend State Model

`ProfileProvider` remains the single UI boundary and exposes the same core
actions plus synchronization status and conversation actions.

Signed out:

- Use the versioned browser profile.
- Keep shortlist, comparison, saved-search drafts, recent views, assistant
  draft, and anonymous conversations local.
- Never call protected endpoints.

Transition to signed in:

1. Wait for Clerk and local-profile hydration.
2. Acquire a Clerk session token with `getToken()`.
3. Submit the idempotent anonymous merge payload.
4. Replace account-owned local state with the authoritative server response.
5. Retain only a minimal in-memory cache for responsive rendering.

Signed in:

- Send a current token on every protected request.
- Apply mutations optimistically.
- Roll back the affected state and expose a recoverable error if persistence
  fails.
- Refetch the workspace after visibility restoration or explicit retry, not on
  a polling interval.

Transition to signed out:

- Clear all account-derived cached data from browser storage and memory.
- Create a fresh anonymous profile identifier.
- Do not copy private account data into the new anonymous profile.

Recent views remain browser-local in this milestone because the requested
server-owned domains are shortlist, comparison, saved searches, and
conversations.

## AI Conversation Compatibility

The current deterministic fixture interpreter persists its messages and
interpreted intent through the conversation API when signed in. Anonymous
messages remain local and are eligible for the one-time merge.

The future LangGraph service will append assistant and buyer turns through the
same repository contract. Model identifiers, provider traces, embeddings, RAG
chunks, and token usage are not part of this milestone and will use separate
tables when that pipeline is designed.

## Error and Availability Behavior

- Clerk or JWKS failure affects only protected endpoints and does not make
  catalogue readiness fail.
- PostgreSQL failure keeps the existing `/ready` behavior unavailable and
  returns sanitized 503 problems for workspace requests.
- A protected mutation that fails leaves the last confirmed state recoverable
  in memory and displays a retryable UI state.
- A missing or expired token triggers a 401 and allows Clerk to refresh the
  session; the frontend retries once with a newly acquired token.
- No protected request is silently downgraded to anonymous ownership.

## Configuration

Backend settings add:

- `CLERK_SECRET_KEY` for SDK/JWKS authentication in development.
- Optional `CLERK_JWT_KEY` for networkless verification.
- `CARVEO_CLERK_AUTHORIZED_PARTIES` as an explicit origin list.

Compose injects Clerk credentials into API and web containers at runtime only.
Example files contain placeholders. CORS allows the `Authorization` and
`X-Request-ID` headers from configured origins.

## Testing and Acceptance

Backend unit and API tests cover:

- Missing, malformed, expired, and unauthorized-party tokens.
- Verified-subject extraction without trusting request payload identity.
- JIT profile creation and ownership isolation.
- Shortlist idempotency, comparison ordering and limits, saved-search
  deduplication, conversation ordering, and hidden foreign resources.
- One-time merge idempotency and concurrent behavior.
- Sanitized problem responses.

PostgreSQL integration tests cover migration upgrade, foreign keys, uniqueness,
indexes, transactions, and repository behavior. SQLite is not a behavioral
substitute.

Frontend tests cover signed-out local behavior, token forwarding, merge and
hydration, optimistic rollback, sign-out clearing, retry behavior, and
conversation persistence. Existing anonymous tests continue to pass.

Contract generation must update the committed OpenAPI and TypeScript schema.
Acceptance requires backend tests, Ruff, strict mypy, frontend tests,
typecheck, production build, contract checks, Docker Compose validation, and a
healthy integrated stack.

## Delivery Boundary

Included:

- Clerk session verification in FastAPI.
- PostgreSQL-backed buyer ownership for the four requested domains.
- Anonymous-to-account merge and frontend integration.
- Migrations, generated contracts, tests, Compose configuration, and logs.

Deferred:

- Full Clerk user-profile synchronization and production deletion webhooks.
- Accounts administration, organizations, roles, and permissions.
- Email alerts and notification delivery.
- LangGraph, RAG, embeddings, reranking, and OpenRouter calls.
- Cross-market localization changes.
