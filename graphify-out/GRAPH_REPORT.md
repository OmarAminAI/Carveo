# Graph Report - Carveo  (2026-09-03)

## Corpus Check
- 175 files · ~235,684 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1278 nodes · 2382 edges · 95 communities (75 shown, 20 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 227 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `96286042`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- create_app
- Fixture-Backed Ingestion Vertical Slice Design
- assistant-workspace.tsx
- devDependencies
- query.ts
- database.py
- profile-provider.tsx
- dependencies
- compilerOptions
- Carveo Buyer Search Refactor - Implementation Plan
- components.json
- Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App
- beat.py
- index.ts
- carveo-core
- anyio_backend
- route.ts
- app/layout.tsx
- carveo_api/__init__.py
- Authenticated Buyer Workspace Design
- next.config.ts
- next-env.d.ts
- Components
- Carveo Codex Guide
- What You Must Do When Invoked
- SqlAlchemyBuyerWorkspaceRepository
- buyer_sql_repository.py
- Listing
- Global Constraints
- schemas.ts
- graphify reference: extra exports and benchmark
- auth-page-shell.tsx
- Carveo
- graphify reference: query, path, explain
- Carveo Backend
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- Carveo Frontend
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- Agent skills
- extraction-spec.md
- frontend/AGENTS.md
- PROVENANCE.md
- proxy.ts
- Global Constraints
- BuyerWorkspaceRepository
- fixture-catalogue.ts
- FakeBuyerRepository
- test_auth.py
- main.py
- buyer_routes.py
- ClerkRequestAuthenticator
- BuyerWorkspaceClient
- test_fresh_postgres_migrates_to_head
- File Structure
- Issue tracker: GitHub
- CONTEXT-MAP.md
- domain.md
- triage-labels.md
- test_buyer_api.py
- fixture-catalogue-repository.ts
- test_models.py
- ValueError
- tasks.py
- test_monitoring.py
- api-catalogue-repository.ts
- buyer-workspace-client.test.ts
- en-ae/layout.tsx
- condition-evidence.tsx
- env.py
- OwnedResourceNotFound
- Ingestion
- FakeClerkClient
- comparison-workspace.tsx
- monitoring.py
- [model]/page.tsx
- HealthMonitor

## God Nodes (most connected - your core abstractions)
1. `SqlAlchemyBuyerWorkspaceRepository` - 50 edges
2. `BuyerWorkspaceRepository` - 36 edges
3. `FakeBuyerRepository` - 33 edges
4. `create_app()` - 32 edges
5. `FixtureCatalogueRepository` - 24 edges
6. `AuthenticatedBuyer` - 23 edges
7. `Fixture-Backed Ingestion Vertical Slice Design` - 23 edges
8. `Listing` - 20 edges
9. `SqlAlchemyCatalogueRepository` - 19 edges
10. `cn()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_production_requires_explicit_clerk_authorized_parties_and_a_verification_key()` --uses--> `Settings`  [INFERRED]
  backend/apps/api/tests/test_auth.py → backend/apps/api/src/carveo_api/settings.py
- `test_buyer_contracts_reject_non_utc_timestamps()` --uses--> `ConversationTurn`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_buyer_workspace_rejects_duplicate_comparison_listing_ids()` --uses--> `BuyerWorkspace`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_buyer_workspace_rejects_more_than_four_comparison_listing_ids()` --uses--> `BuyerWorkspace`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_catalogue_metadata_contains_expected_tables()` --uses--> `Base`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/models.py

## Import Cycles
- None detected.

## Communities (95 total, 20 thin omitted)

### Community 0 - "create_app"
Cohesion: 0.05
Nodes (80): create_app(), client(), anyio, AsyncClient, fixture, ready(), test_detail_compare_and_missing_problem(), test_health_and_readiness_are_distinct() (+72 more)

### Community 1 - "Fixture-Backed Ingestion Vertical Slice Design"
Cohesion: 0.05
Nodes (38): Acceptance Criteria, Architectural Shape, Catalogue Updates, Container integration tests, Crawl4AI Adapter, Crawl-run items, Crawl runs, Delivery Slices (+30 more)

### Community 2 - "assistant-workspace.tsx"
Cohesion: 0.06
Nodes (47): ListingPage(), CarsPage(), metadata, toParams(), metadata, AppHeader(), AssistantWorkspace(), intentHref() (+39 more)

### Community 3 - "devDependencies"
Cohesion: 0.04
Nodes (46): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+38 more)

### Community 4 - "query.ts"
Cohesion: 0.17
Nodes (10): bodyTypes, HomePage(), makeLinks, SearchConsole(), vehicleSuggestions, arrayKeys, numberKeys, parseListingQuery() (+2 more)

### Community 5 - "database.py"
Cohesion: 0.21
Nodes (12): run(), get_settings(), Settings, MonkeyPatch, test_settings_accept_clerk_cli_secret_without_copying_it(), create_engine(), create_session_factory(), async_sessionmaker (+4 more)

### Community 6 - "profile-provider.tsx"
Cohesion: 0.23
Nodes (16): BrowserProfile, addComparison(), createEmptyProfile(), migrateProfile(), PROFILE_STORAGE_KEY, recordRecentView(), removeComparison(), saveSearchDraft() (+8 more)

### Community 7 - "dependencies"
Cohesion: 0.05
Nodes (39): @base-ui/react, class-variance-authority, @clerk/nextjs, @clerk/ui, clsx, embla-carousel-react, @fontsource/barlow-condensed, dependencies (+31 more)

### Community 8 - "compilerOptions"
Cohesion: 0.07
Nodes (27): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+19 more)

### Community 9 - "Carveo Buyer Search Refactor - Implementation Plan"
Cohesion: 0.04
Nodes (45): 10. Test Plan, 11. Observability and Success Metrics, 12. Risks and Mitigations, 13. Review Decisions Needed Before Phase 1, 14. Definition of Done for the First Release, 15. Research References, 1. Purpose and Approval Boundary, 2. Evidence From the Existing Repository (+37 more)

### Community 10 - "components.json"
Cohesion: 0.12
Nodes (15): aliases, components, hooks, lib, ui, utils, iconLibrary, rsc (+7 more)

### Community 11 - "Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App"
Cohesion: 0.05
Nodes (43): 1. Chat Intake, 2. Finding Relevant Listing Pages, 3. Extracting Listing Details, 4. Damage, Accident, Warranty, and Risk Signals, 5. Ranking Top 10 Cars, 6. Saved Searches and Price Drops, Best answer for this application:, CarSwitch / CARS24 (+35 more)

### Community 12 - "beat.py"
Cohesion: 0.14
Nodes (14): AsyncIOScheduler, BeatRuntime, BeatSettings, BeatStore, build_scheduler(), Protocol, Carveo periodic scheduler entry point., record_beat_tick() (+6 more)

### Community 13 - "index.ts"
Cohesion: 0.32
Nodes (4): metadata, CatalogueEnvironment, catalogueRepository, createCatalogueRepository()

### Community 14 - "carveo-core"
Cohesion: 0.83
Nodes (4): carveo-api, carveo-core, carveo-worker, carveo-workspace

### Community 21 - "Authenticated Buyer Workspace Design"
Cohesion: 0.08
Nodes (25): AI Conversation Compatibility, API Contract, Architectural Decision, Authenticated Buyer Workspace Design, `buyer_comparison_items`, `buyer_conversation_turns`, `buyer_conversations`, `buyer_profiles` (+17 more)

### Community 35 - "Components"
Cohesion: 0.05
Nodes (40): aeonikPro — Display headings only — the wordmark 'AuthKit', section headings, hero copy; weight 500 at 44-48px gives the wordmark a wide, calm presence rather than a bold shout · `--font-aeonikpro`, Agent Prompt Guide, Auth-Form Modal Card, Authkit — Style Reference, Background Grid Layer, Badge / Tag, Border Radius, Components (+32 more)

### Community 36 - "Carveo Codex Guide"
Cohesion: 0.07
Nodes (26): Backend, Backend, Backend only, Carveo Codex Guide, Complete integrated stack, Containers and contracts, Contracts and Fixtures, Credential policy (+18 more)

### Community 37 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 38 - "SqlAlchemyBuyerWorkspaceRepository"
Cohesion: 0.09
Nodes (35): _conversation_summary(), AsyncSession, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, SavedSearch (+27 more)

### Community 39 - "buyer_sql_repository.py"
Cohesion: 0.30
Nodes (20): AnonymousWorkspaceMergeRequest, BuyerContractModel, BuyerWorkspace, ComparisonUpdate, Conversation, ConversationCreate, ConversationSummary, ConversationTurn (+12 more)

### Community 40 - "Listing"
Cohesion: 0.19
Nodes (4): Listing, ListingPage, ApiCatalogueRepository, CatalogueRepository

### Community 41 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Authenticated Buyer Workspace Implementation Plan, Global Constraints, Task 1: Clerk Request Authentication Boundary, Task 2: Buyer Contracts, Tables, and Migration, Task 3: SQLAlchemy Buyer Workspace Repository, Task 4: Protected FastAPI Buyer Routes, Task 5: OpenAPI and TypeScript Buyer Contracts, Task 6: Authenticated Frontend Workspace Client (+2 more)

### Community 42 - "schemas.ts"
Cohesion: 0.10
Nodes (24): PriceHistoryChart(), anonymousConversationSchema, assistantTurnSchema, buyerWorkspaceSchema, ComparisonSelection, conversationSchema, ConversationSummary, conversationSummarySchema (+16 more)

### Community 43 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 45 - "Carveo"
Cohesion: 0.29
Nodes (6): Backend, Carveo, Data Boundary, Frontend, Repository, Run Everything

### Community 46 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 47 - "Carveo Backend"
Cohesion: 0.40
Nodes (4): Carveo Backend, Quality, Run, Services

### Community 48 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 49 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 50 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 51 - "Carveo Frontend"
Cohesion: 0.50
Nodes (3): Carveo Frontend, Run locally, Verify

### Community 54 - "Agent skills"
Cohesion: 0.33
Nodes (5): Agent skills, Domain docs, graphify, Issue tracker, Triage labels

### Community 60 - "Global Constraints"
Cohesion: 0.25
Nodes (7): Carveo Observability Foundation Implementation Plan, Global Constraints, Task 1: Health And Metrics Contracts, Task 2: Application Observability, Task 3: Compose And Prometheus Infrastructure, Task 4: Grafana Provisioning, Task 5: Documentation And Live Verification

### Community 61 - "BuyerWorkspaceRepository"
Cohesion: 0.12
Nodes (11): BuyerWorkspaceRepository, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, Protocol, SavedSearch (+3 more)

### Community 62 - "fixture-catalogue.ts"
Cohesion: 0.17
Nodes (10): MarketCharts(), fixtureCatalogue, mediaByBodyType, mediaByModel, Seed, seeds, seedSchema, toListingSearchParams() (+2 more)

### Community 63 - "FakeBuyerRepository"
Cohesion: 0.17
Nodes (10): FakeBuyerRepository, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, SavedSearch, SavedSearchUpsert (+2 more)

### Community 64 - "test_auth.py"
Cohesion: 0.19
Nodes (16): auth_client(), FakeAuthenticator, FakeWorkspaceRepository, anyio, AsyncClient, BuyerWorkspace, fixture, ready() (+8 more)

### Community 65 - "main.py"
Cohesion: 0.17
Nodes (13): Any, AuthenticationError, AuthenticationUnavailableError, Exception, configure_logging(), listing_query(), ListingQuery, problem() (+5 more)

### Community 66 - "buyer_routes.py"
Cohesion: 0.14
Nodes (29): AuthenticatedBuyer, add_shortlist(), append_turn(), buyer_repositories(), conversation_detail(), conversations(), create_conversation(), delete_saved_search() (+21 more)

### Community 67 - "ClerkRequestAuthenticator"
Cohesion: 0.18
Nodes (8): ClerkRequestAuthenticator, Protocol, Request, RequestAuthenticator, require_buyer(), bearer_auth, HTTPAuthorizationCredentials, Security

### Community 68 - "BuyerWorkspaceClient"
Cohesion: 0.21
Nodes (4): BuyerWorkspace, Conversation, SavedSearch, BuyerWorkspaceClient

### Community 69 - "test_fresh_postgres_migrates_to_head"
Cohesion: 0.43
Nodes (7): _check_constraint_names(), _foreign_key_ondelete(), _foreign_key_targets(), _index_names(), test_fresh_postgres_migrates_to_head(), _unique_column_sets(), integration

### Community 70 - "File Structure"
Cohesion: 0.09
Nodes (21): Acceptance Checklist, API, observability, and frontend, File Structure, Fixture-Backed Ingestion Implementation Plan, Fixture origin and media, Global Constraints, Reference Notes, Shared backend domain (+13 more)

### Community 76 - "test_buyer_api.py"
Cohesion: 0.30
Nodes (12): buyer_api(), FakeAuthenticator, anyio, AsyncClient, fixture, Request, test_conversation_routes_preserve_ownership_and_ordered_turn_contract(), test_public_routes_stay_public_and_cors_allows_authorization() (+4 more)

### Community 77 - "fixture-catalogue-repository.ts"
Cohesion: 0.19
Nodes (6): DealPosition, ModelMarketSummary, calculateDealPosition(), median(), FixtureCatalogueRepository, matches()

### Community 78 - "test_models.py"
Cohesion: 0.29
Nodes (9): _check_constraint_names(), _foreign_key_targets(), _index_names(), test_buyer_contracts_reject_non_utc_timestamps(), test_buyer_metadata_enforces_ownership_and_ordering_constraints(), test_buyer_workspace_rejects_duplicate_comparison_listing_ids(), test_buyer_workspace_rejects_more_than_four_comparison_listing_ids(), test_catalogue_metadata_contains_expected_tables() (+1 more)

### Community 79 - "ValueError"
Cohesion: 0.24
Nodes (5): model_validator, model_validator, _require_utc_datetime(), model_validator, ValueError

### Community 80 - "tasks.py"
Cohesion: 0.22
Nodes (12): actor, build_broker(), configure_broker(), Broker, configure_worker_broker(), heartbeat(), Broker, smoke() (+4 more)

### Community 81 - "test_monitoring.py"
Cohesion: 0.20
Nodes (8): Carveo ingestion worker shell., anyio, test_beat_heartbeat_must_be_recent_and_not_from_the_future(), test_beat_tick_uses_a_bounded_redis_ttl(), test_health_monitor_records_failures_without_aborting_the_cycle(), test_http_probe_rejects_unsuccessful_responses(), CollectorRegistry, parametrize

### Community 82 - "api-catalogue-repository.ts"
Cohesion: 0.22
Nodes (8): components, $defs, operations, paths, webhooks, listingPageSchema, modelSummarySchema, parseAllQuery()

### Community 83 - "buyer-workspace-client.test.ts"
Cohesion: 0.29
Nodes (4): applyWorkspace(), emptyWorkspace, toAnonymousMergePayload(), WorkspaceRequestError

### Community 85 - "condition-evidence.tsx"
Cohesion: 0.50
Nodes (3): ConditionEvidencePanel(), groups, ConditionEvidence

### Community 88 - "OwnedResourceNotFound"
Cohesion: 0.67
Nodes (3): OwnedResourceNotFound, A buyer-owned resource is absent or belongs to another buyer., LookupError

### Community 90 - "FakeClerkClient"
Cohesion: 0.27
Nodes (7): FakeClerkClient, Exception, Request, test_clerk_authenticator_maps_sdk_failures_to_unavailable(), test_clerk_authenticator_maps_unsigned_or_malformed_subjects_to_one_authentication_error(), test_clerk_authenticator_returns_only_verified_nonempty_subject(), RequestState

### Community 91 - "comparison-workspace.tsx"
Cohesion: 0.31
Nodes (7): loadComparisonListings(), ComparePage(), metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money()

### Community 92 - "monitoring.py"
Cohesion: 0.33
Nodes (7): check(), is_fresh_heartbeat(), Docker health command for the Carveo scheduler., probe_redis(), probe_worker(), Scheduled health monitoring for Carveo services., Redis

### Community 93 - "[model]/page.tsx"
Cohesion: 0.46
Nodes (5): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), slugifyVehicleName()

### Community 94 - "HealthMonitor"
Cohesion: 0.40
Nodes (3): HealthMonitor, ProbeResult, Probe

## Knowledge Gaps
- **416 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `css` (+411 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `test_auth.py`, `main.py`, `ClerkRequestAuthenticator`, `database.py`, `SqlAlchemyBuyerWorkspaceRepository`, `buyer_sql_repository.py`, `test_buyer_api.py`, `OwnedResourceNotFound`, `BuyerWorkspaceRepository`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `BuyerWorkspaceRepository` connect `BuyerWorkspaceRepository` to `create_app`, `buyer_routes.py`, `buyer_sql_repository.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `create_engine()` connect `database.py` to `create_app`, `beat.py`, `test_fresh_postgres_migrates_to_head`, `SqlAlchemyBuyerWorkspaceRepository`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `SqlAlchemyBuyerWorkspaceRepository` (e.g. with `buyer_repositories()` and `AnonymousWorkspaceMergeRequest`) actually correct?**
  _`SqlAlchemyBuyerWorkspaceRepository` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `BuyerWorkspaceRepository` (e.g. with `add_shortlist()` and `append_turn()`) actually correct?**
  _`BuyerWorkspaceRepository` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `FakeBuyerRepository` (e.g. with `AnonymousWorkspaceMergeRequest` and `BuyerWorkspace`) actually correct?**
  _`FakeBuyerRepository` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `create_app()` (e.g. with `AuthenticationError` and `AuthenticationUnavailableError`) actually correct?**
  _`create_app()` has 16 INFERRED edges - model-reasoned connections that need verification._