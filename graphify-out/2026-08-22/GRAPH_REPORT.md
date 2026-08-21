# Graph Report - Carveo  (2026-08-21)

## Corpus Check
- 157 files · ~215,411 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 899 nodes · 1459 edges · 63 communities (49 shown, 14 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 59 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `64bc93bf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- fixture-catalogue-repository.ts
- [listingId]/page.tsx
- devDependencies
- profile-provider.tsx
- create_app
- schemas.ts
- dependencies
- compilerOptions
- Carveo Buyer Search Refactor - Implementation Plan
- components.json
- Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App
- beat.py
- query.ts
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
- models.py
- index.ts
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
- fixture-catalogue.ts
- cars/page.tsx

## God Nodes (most connected - your core abstractions)
1. `FixtureCatalogueRepository` - 23 edges
2. `create_app()` - 21 edges
3. `Listing` - 20 edges
4. `SqlAlchemyCatalogueRepository` - 19 edges
5. `cn()` - 19 edges
6. `ContractModel` - 16 edges
7. `load_fixture_listings()` - 16 edges
8. `compilerOptions` - 16 edges
9. `Carveo Buyer Search Refactor - Implementation Plan` - 16 edges
10. `CatalogueRepository` - 15 edges

## Surprising Connections (you probably didn't know these)
- `listing_query()` --uses--> `ListingQuery`  [INFERRED]
  backend/apps/api/src/carveo_api/main.py → backend/packages/carveo-core/src/carveo_core/contracts.py
- `create_app()` --uses--> `CatalogueRepository`  [INFERRED]
  backend/apps/api/src/carveo_api/main.py → backend/packages/carveo-core/src/carveo_core/catalogue.py
- `create_app()` --uses--> `CompareRequest`  [INFERRED]
  backend/apps/api/src/carveo_api/main.py → backend/packages/carveo-core/src/carveo_core/contracts.py
- `create_app()` --uses--> `CompareResponse`  [INFERRED]
  backend/apps/api/src/carveo_api/main.py → backend/packages/carveo-core/src/carveo_core/contracts.py
- `create_app()` --uses--> `Listing`  [INFERRED]
  backend/apps/api/src/carveo_api/main.py → backend/packages/carveo-core/src/carveo_core/contracts.py

## Import Cycles
- None detected.

## Communities (63 total, 14 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.07
Nodes (52): CatalogueRepository, FixtureCatalogueRepository, Listing, ListingPage, ListingQuery, Protocol, with_deal_position(), CompareRequest (+44 more)

### Community 1 - "fixture-catalogue-repository.ts"
Cohesion: 0.17
Nodes (7): DealPosition, ListingPage, ModelMarketSummary, calculateDealPosition(), median(), FixtureCatalogueRepository, matches()

### Community 2 - "[listingId]/page.tsx"
Cohesion: 0.07
Nodes (35): ListingPage(), metadata, AppHeader(), AssistantWorkspace(), intentHref(), AuthControls(), AuthControlsProps, CompareButton() (+27 more)

### Community 3 - "devDependencies"
Cohesion: 0.04
Nodes (46): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+38 more)

### Community 4 - "profile-provider.tsx"
Cohesion: 0.22
Nodes (15): dynamic, AppFooter(), BrowserProfile, addComparison(), createEmptyProfile(), migrateProfile(), PROFILE_STORAGE_KEY, recordRecentView() (+7 more)

### Community 5 - "create_app"
Cohesion: 0.07
Nodes (37): Any, async_sessionmaker, configure_logging(), create_app(), listing_query(), ListingQuery, problem(), validation_problem() (+29 more)

### Community 6 - "schemas.ts"
Cohesion: 0.18
Nodes (10): ConditionEvidencePanel(), groups, PriceHistoryChart(), AssistantTurn, ComparisonSelection, ConditionEvidence, dealPositionSchema, ListingSort (+2 more)

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

### Community 13 - "query.ts"
Cohesion: 0.18
Nodes (10): bodyTypes, HomePage(), makeLinks, SearchConsole(), vehicleSuggestions, arrayKeys, numberKeys, parseListingQuery() (+2 more)

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
Cohesion: 0.08
Nodes (25): Backend, Backend, Backend only, Carveo Codex Guide, Complete integrated stack, Containers and contracts, Contracts and Fixtures, Credential policy (+17 more)

### Community 37 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 38 - "models.py"
Cohesion: 0.23
Nodes (14): do_run_migrations(), run_async_migrations(), Base, ConditionEvidenceRecord, DuplicateOfferRecord, ListingPhoto, ListingRecord, PriceObservationRecord (+6 more)

### Community 39 - "index.ts"
Cohesion: 0.18
Nodes (9): metadata, metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money(), CatalogueEnvironment, catalogueRepository (+1 more)

### Community 40 - "Listing"
Cohesion: 0.19
Nodes (5): loadComparisonListings(), ComparePage(), Listing, ApiCatalogueRepository, CatalogueRepository

### Community 41 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Authenticated Buyer Workspace Implementation Plan, Global Constraints, Task 1: Clerk Request Authentication Boundary, Task 2: Buyer Contracts, Tables, and Migration, Task 3: SQLAlchemy Buyer Workspace Repository, Task 4: Protected FastAPI Buyer Routes, Task 5: OpenAPI and TypeScript Buyer Contracts, Task 6: Authenticated Frontend Workspace Client (+2 more)

### Community 42 - "api-catalogue-repository.ts"
Cohesion: 0.22
Nodes (8): components, $defs, operations, paths, webhooks, listingPageSchema, modelSummarySchema, parseAllQuery()

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

### Community 61 - "fixture-catalogue.ts"
Cohesion: 0.15
Nodes (14): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), MarketCharts(), fixtureCatalogue, mediaByBodyType, mediaByModel (+6 more)

### Community 62 - "cars/page.tsx"
Cohesion: 0.31
Nodes (8): CarsPage(), metadata, toParams(), FilterFields(), options, MobileFilterDrawer(), toListingSearchParams(), ListingQuery

## Knowledge Gaps
- **341 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `css` (+336 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `contracts.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `client()` connect `create_app` to `contracts.py`, `beat.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `create_engine()` connect `create_app` to `beat.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `FixtureCatalogueRepository` (e.g. with `client()` and `test_unexpected_failures_are_sanitized()`) actually correct?**
  _`FixtureCatalogueRepository` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `create_app()` (e.g. with `CatalogueRepository` and `CompareRequest`) actually correct?**
  _`create_app()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `SqlAlchemyCatalogueRepository` (e.g. with `create_app()` and `CompareRequest`) actually correct?**
  _`SqlAlchemyCatalogueRepository` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `style`, `rsc` to the rest of the system?**
  _341 weakly-connected nodes found - possible documentation gaps or missing edges._