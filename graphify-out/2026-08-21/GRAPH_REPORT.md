# Graph Report - Carveo  (2026-08-21)

## Corpus Check
- 141 files · ~205,842 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 788 nodes · 1304 edges · 59 communities (46 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `07f7ae92`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
- fixture-catalogue-repository.ts
- assistant-workspace.tsx
- devDependencies
- profile-provider.tsx
- models.py
- schemas.ts
- dependencies
- compilerOptions
- Carveo Buyer Search Refactor - Implementation Plan
- components.json
- Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App
- configure_worker_broker
- test_api.py
- carveo-core
- anyio_backend
- route.ts
- app/layout.tsx
- carveo_api/__init__.py
- carveo_worker/__init__.py
- next.config.ts
- next-env.d.ts
- Components
- Carveo Codex Guide
- What You Must Do When Invoked
- cars/page.tsx
- index.ts
- Listing
- catalogue-repository.ts
- comparison-workspace.tsx
- graphify reference: extra exports and benchmark
- api-catalogue-repository.ts
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

## God Nodes (most connected - your core abstractions)
1. `FixtureCatalogueRepository` - 23 edges
2. `create_app()` - 21 edges
3. `Listing` - 20 edges
4. `SqlAlchemyCatalogueRepository` - 19 edges
5. `cn()` - 17 edges
6. `ContractModel` - 16 edges
7. `load_fixture_listings()` - 16 edges
8. `compilerOptions` - 16 edges
9. `Carveo Buyer Search Refactor - Implementation Plan` - 16 edges
10. `CatalogueRepository` - 15 edges

## Surprising Connections (you probably didn't know these)
- `client()` --uses--> `FixtureCatalogueRepository`  [INFERRED]
  backend/apps/api/tests/test_api.py → backend/packages/carveo-core/src/carveo_core/catalogue.py
- `test_query_rejects_invalid_range()` --uses--> `ListingQuery`  [INFERRED]
  backend/packages/carveo-core/tests/test_catalogue.py → backend/packages/carveo-core/src/carveo_core/contracts.py
- `test_catalogue_metadata_contains_expected_tables()` --uses--> `Base`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/models.py
- `_options()` --uses--> `ListingRecord`  [INFERRED]
  backend/packages/carveo-core/src/carveo_core/sql_repository.py → backend/packages/carveo-core/src/carveo_core/models.py
- `record_to_contract()` --uses--> `ListingRecord`  [INFERRED]
  backend/packages/carveo-core/src/carveo_core/sql_repository.py → backend/packages/carveo-core/src/carveo_core/models.py

## Import Cycles
- None detected.

## Communities (59 total, 13 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.05
Nodes (66): Any, configure_logging(), create_app(), listing_query(), ListingQuery, problem(), validation_problem(), test_unexpected_failures_are_sanitized() (+58 more)

### Community 1 - "fixture-catalogue-repository.ts"
Cohesion: 0.21
Nodes (5): DealPosition, ModelMarketSummary, calculateDealPosition(), median(), FixtureCatalogueRepository

### Community 2 - "assistant-workspace.tsx"
Cohesion: 0.10
Nodes (23): metadata, dynamic, AppFooter(), AppHeader(), AssistantWorkspace(), intentHref(), CompareTray(), EmptyState() (+15 more)

### Community 3 - "devDependencies"
Cohesion: 0.04
Nodes (46): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+38 more)

### Community 4 - "profile-provider.tsx"
Cohesion: 0.10
Nodes (28): ListingPage(), CompareButton(), ConditionEvidencePanel(), groups, DealPosition(), RecentViewRecorder(), SaveSearchButton(), ShortlistButton() (+20 more)

### Community 5 - "models.py"
Cohesion: 0.10
Nodes (27): async_sessionmaker, AsyncEngine, do_run_migrations(), run_async_migrations(), run(), get_settings(), model_validator, Settings (+19 more)

### Community 6 - "schemas.ts"
Cohesion: 0.11
Nodes (21): HomePage(), PriceHistoryChart(), fixtureCatalogue, mediaByBodyType, mediaByModel, Seed, seeds, seedSchema (+13 more)

### Community 7 - "dependencies"
Cohesion: 0.06
Nodes (35): @base-ui/react, class-variance-authority, clsx, embla-carousel-react, @fontsource/barlow-condensed, dependencies, @base-ui/react, class-variance-authority (+27 more)

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

### Community 12 - "configure_worker_broker"
Cohesion: 0.23
Nodes (10): actor, build_broker(), configure_broker(), Broker, configure_worker_broker(), Broker, smoke(), test_failed_actor_is_dead_lettered_after_retry_exhaustion() (+2 more)

### Community 13 - "test_api.py"
Cohesion: 0.38
Nodes (9): AsyncClient, client(), anyio, fixture, ready(), test_detail_compare_and_missing_problem(), test_health_and_readiness_are_distinct(), test_invalid_range_is_problem_response() (+1 more)

### Community 14 - "carveo-core"
Cohesion: 0.83
Nodes (4): carveo-api, carveo-core, carveo-worker, carveo-workspace

### Community 35 - "Components"
Cohesion: 0.05
Nodes (40): aeonikPro — Display headings only — the wordmark 'AuthKit', section headings, hero copy; weight 500 at 44-48px gives the wordmark a wide, calm presence rather than a bold shout · `--font-aeonikpro`, Agent Prompt Guide, Auth-Form Modal Card, Authkit — Style Reference, Background Grid Layer, Badge / Tag, Border Radius, Components (+32 more)

### Community 36 - "Carveo Codex Guide"
Cohesion: 0.08
Nodes (25): Backend, Backend, Backend only, Carveo Codex Guide, Complete integrated stack, Containers and contracts, Contracts and Fixtures, Credential policy (+17 more)

### Community 37 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 38 - "cars/page.tsx"
Cohesion: 0.21
Nodes (10): CarsPage(), metadata, toParams(), FilterFields(), options, MobileFilterDrawer(), toListingSearchParams(), ListingPage (+2 more)

### Community 39 - "index.ts"
Cohesion: 0.17
Nodes (8): bodyTypes, makeLinks, metadata, SearchConsole(), vehicleSuggestions, CatalogueEnvironment, catalogueRepository, createCatalogueRepository()

### Community 40 - "Listing"
Cohesion: 0.22
Nodes (4): Listing, ApiCatalogueRepository, parseAllQuery(), CatalogueRepository

### Community 41 - "catalogue-repository.ts"
Cohesion: 0.27
Nodes (6): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), MarketCharts(), slugifyVehicleName()

### Community 42 - "comparison-workspace.tsx"
Cohesion: 0.27
Nodes (7): loadComparisonListings(), ComparePage(), metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money()

### Community 43 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 44 - "api-catalogue-repository.ts"
Cohesion: 0.25
Nodes (7): components, $defs, operations, paths, webhooks, listingPageSchema, modelSummarySchema

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

## Knowledge Gaps
- **302 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `css` (+297 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App` connect `Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App` to `Carveo Buyer Search Refactor - Implementation Plan`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Why does `create_app()` connect `contracts.py` to `test_api.py`, `models.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `FixtureCatalogueRepository` (e.g. with `client()` and `test_unexpected_failures_are_sanitized()`) actually correct?**
  _`FixtureCatalogueRepository` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `create_app()` (e.g. with `CatalogueRepository` and `CompareRequest`) actually correct?**
  _`create_app()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `SqlAlchemyCatalogueRepository` (e.g. with `create_app()` and `CompareRequest`) actually correct?**
  _`SqlAlchemyCatalogueRepository` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `style`, `rsc` to the rest of the system?**
  _302 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `contracts.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05146520146520146 - nodes in this community are weakly interconnected._