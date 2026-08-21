# Graph Report - Carveo  (2026-08-22)

## Corpus Check
- 168 files · ~227,276 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1201 nodes · 2312 edges · 76 communities (61 shown, 15 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 227 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6574b56b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- create_app
- fixture-catalogue-repository.ts
- assistant-workspace.tsx
- devDependencies
- profile-provider.tsx
- test_fresh_postgres_migrates_to_head
- schemas.ts
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
- comparison-workspace.tsx
- Listing
- Global Constraints
- api-catalogue-repository.ts
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
- AGENTS.md
- extraction-spec.md
- frontend/AGENTS.md
- PROVENANCE.md
- proxy.ts
- Global Constraints
- catalogue-repository.ts
- ListingQuery
- FakeBuyerRepository
- test_auth.py
- main.py
- BuyerWorkspaceRepository
- AuthenticatedBuyer
- [listingId]/page.tsx
- cars/page.tsx
- app-header.tsx
- replace_comparison
- FixtureCatalogueRepository
- create_conversation

## God Nodes (most connected - your core abstractions)
1. `SqlAlchemyBuyerWorkspaceRepository` - 50 edges
2. `BuyerWorkspaceRepository` - 36 edges
3. `FakeBuyerRepository` - 33 edges
4. `create_app()` - 32 edges
5. `FixtureCatalogueRepository` - 24 edges
6. `AuthenticatedBuyer` - 23 edges
7. `Listing` - 20 edges
8. `SqlAlchemyCatalogueRepository` - 19 edges
9. `cn()` - 19 edges
10. `BuyerWorkspaceClient` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_production_requires_explicit_clerk_authorized_parties_and_a_verification_key()` --uses--> `Settings`  [INFERRED]
  backend/apps/api/tests/test_auth.py → backend/apps/api/src/carveo_api/settings.py
- `add_shortlist()` --uses--> `AuthenticatedBuyer`  [INFERRED]
  backend/apps/api/src/carveo_api/buyer_routes.py → backend/apps/api/src/carveo_api/auth.py
- `append_turn()` --uses--> `AuthenticatedBuyer`  [INFERRED]
  backend/apps/api/src/carveo_api/buyer_routes.py → backend/apps/api/src/carveo_api/auth.py
- `conversation_detail()` --uses--> `AuthenticatedBuyer`  [INFERRED]
  backend/apps/api/src/carveo_api/buyer_routes.py → backend/apps/api/src/carveo_api/auth.py
- `conversations()` --uses--> `AuthenticatedBuyer`  [INFERRED]
  backend/apps/api/src/carveo_api/buyer_routes.py → backend/apps/api/src/carveo_api/auth.py

## Import Cycles
- None detected.

## Communities (76 total, 15 thin omitted)

### Community 0 - "create_app"
Cohesion: 0.05
Nodes (71): create_app(), client(), anyio, AsyncClient, fixture, ready(), test_detail_compare_and_missing_problem(), test_health_and_readiness_are_distinct() (+63 more)

### Community 1 - "fixture-catalogue-repository.ts"
Cohesion: 0.29
Nodes (5): DealPosition, ModelMarketSummary, calculateDealPosition(), median(), matches()

### Community 2 - "assistant-workspace.tsx"
Cohesion: 0.16
Nodes (16): metadata, AssistantWorkspace(), intentHref(), newId(), profile, Badge(), Bubble(), Marker() (+8 more)

### Community 3 - "devDependencies"
Cohesion: 0.04
Nodes (46): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+38 more)

### Community 4 - "profile-provider.tsx"
Cohesion: 0.14
Nodes (22): AnonymousConversation, anonymousConversationSchema, addComparison(), createEmptyProfile(), migrateProfile(), PROFILE_STORAGE_KEY, recordRecentView(), removeComparison() (+14 more)

### Community 5 - "test_fresh_postgres_migrates_to_head"
Cohesion: 0.11
Nodes (20): do_run_migrations(), run_async_migrations(), run(), get_settings(), model_validator, Settings, _check_constraint_names(), _foreign_key_ondelete() (+12 more)

### Community 6 - "schemas.ts"
Cohesion: 0.06
Nodes (37): ConditionEvidencePanel(), groups, PriceHistoryChart(), components, $defs, operations, paths, webhooks (+29 more)

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
Cohesion: 0.05
Nodes (44): actor, AsyncIOScheduler, BeatRuntime, BeatSettings, BeatStore, build_scheduler(), check(), is_fresh_heartbeat() (+36 more)

### Community 13 - "index.ts"
Cohesion: 0.13
Nodes (10): bodyTypes, makeLinks, metadata, SearchConsole(), vehicleSuggestions, ShortlistWorkspace(), Tab, tabs (+2 more)

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
Cohesion: 0.06
Nodes (82): AnonymousWorkspaceMergeRequest, BuyerContractModel, BuyerWorkspace, ComparisonUpdate, Conversation, ConversationCreate, ConversationSummary, ConversationTurn (+74 more)

### Community 39 - "comparison-workspace.tsx"
Cohesion: 0.27
Nodes (7): loadComparisonListings(), ComparePage(), metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money()

### Community 40 - "Listing"
Cohesion: 0.23
Nodes (3): Listing, ApiCatalogueRepository, CatalogueRepository

### Community 41 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Authenticated Buyer Workspace Implementation Plan, Global Constraints, Task 1: Clerk Request Authentication Boundary, Task 2: Buyer Contracts, Tables, and Migration, Task 3: SQLAlchemy Buyer Workspace Repository, Task 4: Protected FastAPI Buyer Routes, Task 5: OpenAPI and TypeScript Buyer Contracts, Task 6: Authenticated Frontend Workspace Client (+2 more)

### Community 42 - "api-catalogue-repository.ts"
Cohesion: 0.13
Nodes (17): HomePage(), mediaByBodyType, mediaByModel, Seed, seeds, seedSchema, arrayKeys, numberKeys (+9 more)

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

### Community 60 - "Global Constraints"
Cohesion: 0.25
Nodes (7): Carveo Observability Foundation Implementation Plan, Global Constraints, Task 1: Health And Metrics Contracts, Task 2: Application Observability, Task 3: Compose And Prometheus Infrastructure, Task 4: Grafana Provisioning, Task 5: Documentation And Live Verification

### Community 61 - "catalogue-repository.ts"
Cohesion: 0.27
Nodes (6): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), MarketCharts(), slugifyVehicleName()

### Community 62 - "ListingQuery"
Cohesion: 0.32
Nodes (5): FilterFields(), options, MobileFilterDrawer(), ListingPage, ListingQuery

### Community 63 - "FakeBuyerRepository"
Cohesion: 0.14
Nodes (18): FakeBuyerRepository, anyio, AsyncClient, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate (+10 more)

### Community 64 - "test_auth.py"
Cohesion: 0.12
Nodes (25): auth_client(), FakeAuthenticator, FakeClerkClient, FakeWorkspaceRepository, anyio, AsyncClient, BuyerWorkspace, Exception (+17 more)

### Community 65 - "main.py"
Cohesion: 0.14
Nodes (21): Any, Protocol, RequestAuthenticator, append_turn(), buyer_repositories(), conversation_detail(), delete_saved_search(), Conversation (+13 more)

### Community 66 - "BuyerWorkspaceRepository"
Cohesion: 0.12
Nodes (11): BuyerWorkspaceRepository, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, Protocol, SavedSearch (+3 more)

### Community 67 - "AuthenticatedBuyer"
Cohesion: 0.17
Nodes (12): AuthenticatedBuyer, AuthenticationError, AuthenticationUnavailableError, ClerkRequestAuthenticator, Exception, Request, require_buyer(), FakeAuthenticator (+4 more)

### Community 68 - "[listingId]/page.tsx"
Cohesion: 0.23
Nodes (8): CompareButton(), DealPosition(), RecentViewRecorder(), ShortlistButton(), VehicleCard(), VehicleGallery(), fixtureCatalogue, useProfile()

### Community 69 - "cars/page.tsx"
Cohesion: 0.21
Nodes (10): ListingPage(), CarsPage(), metadata, toParams(), CompareTray(), EmptyState(), SaveSearchButton(), Button() (+2 more)

### Community 70 - "app-header.tsx"
Cohesion: 0.24
Nodes (6): dynamic, AppFooter(), AppHeader(), AuthControls(), AuthControlsProps, MobileNavigation()

### Community 71 - "replace_comparison"
Cohesion: 0.22
Nodes (10): add_shortlist(), conversations(), BuyerWorkspace, ConversationSummary, remove_shortlist(), replace_comparison(), workspace(), ComparisonUpdate (+2 more)

### Community 73 - "create_conversation"
Cohesion: 0.22
Nodes (9): create_conversation(), merge_workspace(), ConversationCreate, SavedSearch, SavedSearchUpsert, WorkspaceMergeResponse, saved_searches(), upsert_saved_search() (+1 more)

## Knowledge Gaps
- **355 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `css` (+350 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `test_auth.py`, `main.py`, `BuyerWorkspaceRepository`, `AuthenticatedBuyer`, `test_fresh_postgres_migrates_to_head`, `SqlAlchemyBuyerWorkspaceRepository`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `BuyerWorkspaceRepository` connect `BuyerWorkspaceRepository` to `create_app`, `main.py`, `SqlAlchemyBuyerWorkspaceRepository`, `replace_comparison`, `create_conversation`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `create_engine()` connect `test_fresh_postgres_migrates_to_head` to `create_app`, `beat.py`, `SqlAlchemyBuyerWorkspaceRepository`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `SqlAlchemyBuyerWorkspaceRepository` (e.g. with `buyer_repositories()` and `AnonymousWorkspaceMergeRequest`) actually correct?**
  _`SqlAlchemyBuyerWorkspaceRepository` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `BuyerWorkspaceRepository` (e.g. with `add_shortlist()` and `append_turn()`) actually correct?**
  _`BuyerWorkspaceRepository` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `FakeBuyerRepository` (e.g. with `AnonymousWorkspaceMergeRequest` and `BuyerWorkspace`) actually correct?**
  _`FakeBuyerRepository` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `create_app()` (e.g. with `AuthenticationError` and `AuthenticationUnavailableError`) actually correct?**
  _`create_app()` has 16 INFERRED edges - model-reasoned connections that need verification._