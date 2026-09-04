# Graph Report - Carveo  (2026-09-04)

## Corpus Check
- 202 files · ~248,356 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1627 nodes · 3438 edges · 102 communities (82 shown, 20 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 392 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3eab6628`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- FixtureCatalogueRepository
- Fixture-Backed Ingestion Vertical Slice Design
- assistant-workspace.tsx
- devDependencies
- fixture-catalogue.ts
- index.ts
- profile-provider.tsx
- dependencies
- compilerOptions
- Carveo Buyer Search Refactor - Implementation Plan
- components.json
- Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App
- beat.py
- [listingId]/page.tsx
- carveo-core
- anyio_backend
- route.ts
- app/layout.tsx
- carveo_api/__init__.py
- test_media.py
- Authenticated Buyer Workspace Design
- next.config.ts
- next-env.d.ts
- Components
- Carveo Codex Guide
- What You Must Do When Invoked
- SqlAlchemyBuyerWorkspaceRepository
- test_fixture_corpus.py
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
- buyer_sql_repository.py
- SqlAlchemyIngestionRepository
- FakeBuyerRepository
- ingestion_contracts.py
- main.py
- buyer_routes.py
- BuyerWorkspaceRepository
- cars/page.tsx
- OwnedResourceNotFound
- File Structure
- Issue tracker: GitHub
- CONTEXT-MAP.md
- domain.md
- triage-labels.md
- test_buyer_repository.py
- fixture-catalogue-repository.ts
- test_fresh_postgres_migrates_to_head
- create_app
- BuyerWorkspaceClient
- SqlAlchemyCatalogueRepository
- contracts.py
- AuthenticatedBuyer
- query.ts
- test_media_api.py
- app-header.tsx
- normalize_listing
- Ingestion
- test_auth.py
- comparison-workspace.tsx
- test_api.py
- catalogue-repository.ts
- ListingQuery
- test_models.py
- upsert_saved_search
- calculate_deal_position
- replace_comparison
- WorkerSettings
- condition-evidence.tsx
- init.sh

## God Nodes (most connected - your core abstractions)
1. `SqlAlchemyBuyerWorkspaceRepository` - 50 edges
2. `SqlAlchemyIngestionRepository` - 44 edges
3. `_datetime()` - 38 edges
4. `create_app()` - 37 edges
5. `BuyerWorkspaceRepository` - 36 edges
6. `FakeBuyerRepository` - 33 edges
7. `normalize_listing()` - 31 edges
8. `ListingReference` - 27 edges
9. `FixtureCatalogueRepository` - 26 edges
10. `ListingRecord` - 25 edges

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

## Communities (102 total, 20 thin omitted)

### Community 0 - "FixtureCatalogueRepository"
Cohesion: 0.16
Nodes (12): CatalogueRepository, FixtureCatalogueRepository, Listing, ListingPage, ListingQuery, Protocol, CompareRequest, CompareResponse (+4 more)

### Community 1 - "Fixture-Backed Ingestion Vertical Slice Design"
Cohesion: 0.05
Nodes (38): Acceptance Criteria, Architectural Shape, Catalogue Updates, Container integration tests, Crawl4AI Adapter, Crawl-run items, Crawl runs, Delivery Slices (+30 more)

### Community 2 - "assistant-workspace.tsx"
Cohesion: 0.16
Nodes (16): metadata, AssistantWorkspace(), intentHref(), newId(), profile, Badge(), Bubble(), Marker() (+8 more)

### Community 3 - "devDependencies"
Cohesion: 0.04
Nodes (46): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+38 more)

### Community 4 - "fixture-catalogue.ts"
Cohesion: 0.18
Nodes (9): MarketCharts(), fixtureCatalogue, mediaByBodyType, mediaByModel, Seed, seeds, seedSchema, conditionEvidenceSchema (+1 more)

### Community 5 - "index.ts"
Cohesion: 0.32
Nodes (4): metadata, CatalogueEnvironment, catalogueRepository, createCatalogueRepository()

### Community 6 - "profile-provider.tsx"
Cohesion: 0.17
Nodes (20): BrowserProfile, addComparison(), createEmptyProfile(), migrateProfile(), PROFILE_STORAGE_KEY, recordRecentView(), removeComparison(), saveSearchDraft() (+12 more)

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

### Community 13 - "[listingId]/page.tsx"
Cohesion: 0.12
Nodes (17): ListingPage(), CompareButton(), CompareTray(), DealPosition(), EmptyState(), RecentViewRecorder(), SaveSearchButton(), ShortlistButton() (+9 more)

### Community 14 - "carveo-core"
Cohesion: 0.83
Nodes (4): carveo-api, carveo-core, carveo-worker, carveo-workspace

### Community 20 - "test_media.py"
Cohesion: 0.08
Nodes (32): MediaCacheResult, _DownloadedPhoto, _failed(), MediaCache, MediaValidationError, AsyncClient, UUID, ValueError (+24 more)

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
Cohesion: 0.14
Nodes (20): _conversation_summary(), AsyncSession, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, SavedSearch (+12 more)

### Community 39 - "test_fixture_corpus.py"
Cohesion: 0.39
Nodes (5): load_manifest(), test_baseline_contains_twelve_unique_listings_and_a_cross_page_duplicate(), test_every_manifest_page_exists_and_uses_private_fixture_origin(), test_failure_scenario_covers_expected_failure_classes(), test_manifest_defines_immutable_lifecycle_scenarios()

### Community 40 - "Listing"
Cohesion: 0.16
Nodes (8): paths, Listing, ListingPage, ApiCatalogueRepository, listingPageSchema, modelSummarySchema, parseAllQuery(), CatalogueRepository

### Community 41 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Authenticated Buyer Workspace Implementation Plan, Global Constraints, Task 1: Clerk Request Authentication Boundary, Task 2: Buyer Contracts, Tables, and Migration, Task 3: SQLAlchemy Buyer Workspace Repository, Task 4: Protected FastAPI Buyer Routes, Task 5: OpenAPI and TypeScript Buyer Contracts, Task 6: Authenticated Frontend Workspace Client (+2 more)

### Community 42 - "schemas.ts"
Cohesion: 0.07
Nodes (31): PriceHistoryChart(), components, $defs, operations, webhooks, AnonymousConversation, anonymousConversationSchema, AssistantTurn (+23 more)

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

### Community 61 - "buyer_sql_repository.py"
Cohesion: 0.20
Nodes (20): AnonymousWorkspaceMergeRequest, BuyerContractModel, BuyerWorkspace, ComparisonUpdate, Conversation, ConversationCreate, ConversationSummary, ConversationTurn (+12 more)

### Community 62 - "SqlAlchemyIngestionRepository"
Cohesion: 0.08
Nodes (71): _datetime(), CachedPhotoWrite, CrawlRunSummary, model_validator, RunStatus, CreateRun, IngestionModel, IngestionRepository (+63 more)

### Community 63 - "FakeBuyerRepository"
Cohesion: 0.12
Nodes (20): FakeBuyerRepository, anyio, AsyncClient, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate (+12 more)

### Community 64 - "ingestion_contracts.py"
Cohesion: 0.05
Nodes (70): CrawlRunItemResult, ListingReference, NormalizedConditionEvidence, NormalizedPhoto, BaseModel, RawConditionClaim, RawListing, RawPhoto (+62 more)

### Community 65 - "main.py"
Cohesion: 0.13
Nodes (13): AuthenticationError, AuthenticationUnavailableError, Exception, main(), configure_logging(), listing_query(), ListingQuery, FakeAuthenticator (+5 more)

### Community 66 - "buyer_routes.py"
Cohesion: 0.18
Nodes (19): append_turn(), buyer_repositories(), conversation_detail(), create_conversation(), delete_saved_search(), merge_workspace(), Conversation, ConversationCreate (+11 more)

### Community 67 - "BuyerWorkspaceRepository"
Cohesion: 0.14
Nodes (10): BuyerWorkspaceRepository, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, Protocol, SavedSearch (+2 more)

### Community 68 - "cars/page.tsx"
Cohesion: 0.31
Nodes (8): CarsPage(), metadata, toParams(), FilterFields(), options, MobileFilterDrawer(), toListingSearchParams(), ListingQuery

### Community 69 - "OwnedResourceNotFound"
Cohesion: 0.67
Nodes (3): OwnedResourceNotFound, LookupError, A buyer-owned resource is absent or belongs to another buyer.

### Community 70 - "File Structure"
Cohesion: 0.09
Nodes (21): Acceptance Checklist, API, observability, and frontend, File Structure, Fixture-Backed Ingestion Implementation Plan, Fixture origin and media, Global Constraints, Reference Notes, Shared backend domain (+13 more)

### Community 76 - "test_buyer_repository.py"
Cohesion: 0.18
Nodes (20): SavedSearchUpsert, anyio_backend(), _AsyncRendezvous, _clear_buyers(), postgres_database_url(), async_sessionmaker, AsyncSession, fixture (+12 more)

### Community 77 - "fixture-catalogue-repository.ts"
Cohesion: 0.19
Nodes (6): DealPosition, ModelMarketSummary, calculateDealPosition(), median(), FixtureCatalogueRepository, matches()

### Community 78 - "test_fresh_postgres_migrates_to_head"
Cohesion: 0.11
Nodes (20): do_run_migrations(), run_async_migrations(), run(), get_settings(), BaseSettings, model_validator, Settings, _check_constraint_names() (+12 more)

### Community 79 - "create_app"
Cohesion: 0.14
Nodes (14): create_app(), DatabaseMediaService, MediaAsset, MediaService, ObjectReader, async_sessionmaker, AsyncSession, Protocol (+6 more)

### Community 80 - "BuyerWorkspaceClient"
Cohesion: 0.21
Nodes (4): BuyerWorkspace, Conversation, SavedSearch, BuyerWorkspaceClient

### Community 82 - "SqlAlchemyCatalogueRepository"
Cohesion: 0.27
Nodes (10): with_deal_position(), _options(), AsyncSession, Listing, ListingPage, ListingQuery, record_to_contract(), SqlAlchemyCatalogueRepository (+2 more)

### Community 83 - "contracts.py"
Cohesion: 0.28
Nodes (14): ConditionEvidence, ContractModel, DuplicateOffer, FixtureSeed, Listing, Market, PriceObservation, BaseModel (+6 more)

### Community 84 - "AuthenticatedBuyer"
Cohesion: 0.17
Nodes (11): AuthenticatedBuyer, ClerkRequestAuthenticator, Protocol, Request, RequestAuthenticator, require_buyer(), FakeAuthenticator, Request (+3 more)

### Community 85 - "query.ts"
Cohesion: 0.18
Nodes (10): bodyTypes, HomePage(), makeLinks, SearchConsole(), vehicleSuggestions, arrayKeys, numberKeys, parseListingQuery() (+2 more)

### Community 86 - "test_media_api.py"
Cohesion: 0.28
Nodes (11): client(), anyio, AsyncClient, fixture, UUID, StubMediaService, test_media_openapi_contract_declares_binary_image_responses(), test_media_proxy_returns_bytes_type_etag_and_immutable_cache_headers() (+3 more)

### Community 87 - "app-header.tsx"
Cohesion: 0.24
Nodes (6): dynamic, AppFooter(), AppHeader(), AuthControls(), AuthControlsProps, MobileNavigation()

### Community 88 - "normalize_listing"
Cohesion: 0.09
Nodes (49): NormalizedListing, canonicalize_source_url(), ValueError, resolve_source_identity(), SourceIdentity, SourceIdentityError, _alias_key(), NormalizationError (+41 more)

### Community 90 - "test_auth.py"
Cohesion: 0.12
Nodes (25): auth_client(), FakeClerkClient, FakeWorkspaceRepository, anyio, AsyncClient, BuyerWorkspace, Exception, fixture (+17 more)

### Community 91 - "comparison-workspace.tsx"
Cohesion: 0.27
Nodes (7): loadComparisonListings(), ComparePage(), metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money()

### Community 92 - "test_api.py"
Cohesion: 0.33
Nodes (11): client(), anyio, AsyncClient, fixture, ready(), test_detail_compare_and_missing_problem(), test_health_and_readiness_are_distinct(), test_invalid_range_is_problem_response() (+3 more)

### Community 93 - "catalogue-repository.ts"
Cohesion: 0.42
Nodes (5): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), slugifyVehicleName()

### Community 94 - "ListingQuery"
Cohesion: 0.27
Nodes (10): ListingQuery, model_validator, anyio, fixture, repository(), test_compare_preserves_order_and_reports_missing(), test_filters_sorts_and_paginates(), test_query_rejects_invalid_range() (+2 more)

### Community 95 - "test_models.py"
Cohesion: 0.29
Nodes (9): _check_constraint_names(), _foreign_key_targets(), _index_names(), test_buyer_contracts_reject_non_utc_timestamps(), test_buyer_metadata_enforces_ownership_and_ordering_constraints(), test_buyer_workspace_rejects_duplicate_comparison_listing_ids(), test_buyer_workspace_rejects_more_than_four_comparison_listing_ids(), test_catalogue_metadata_contains_expected_tables() (+1 more)

### Community 96 - "upsert_saved_search"
Cohesion: 0.25
Nodes (8): conversations(), ConversationSummary, SavedSearch, SavedSearchUpsert, saved_searches(), upsert_saved_search(), workspace(), get

### Community 97 - "calculate_deal_position"
Cohesion: 0.48
Nodes (5): DealPosition, calculate_deal_position(), test_deal_position_reports_below_typical_price(), test_deal_position_requires_three_comparables(), DealPosition

### Community 98 - "replace_comparison"
Cohesion: 0.40
Nodes (6): add_shortlist(), BuyerWorkspace, remove_shortlist(), replace_comparison(), ComparisonUpdate, put

### Community 100 - "condition-evidence.tsx"
Cohesion: 0.50
Nodes (3): ConditionEvidencePanel(), groups, ConditionEvidence

## Knowledge Gaps
- **417 isolated node(s):** `init.sh script`, `$schema`, `style`, `rsc`, `tsx` (+412 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_datetime()` connect `SqlAlchemyIngestionRepository` to `ingestion_contracts.py`, `SqlAlchemyBuyerWorkspaceRepository`, `contracts.py`, `test_media.py`, `normalize_listing`, `buyer_sql_repository.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `create_app()` connect `create_app` to `FixtureCatalogueRepository`, `main.py`, `buyer_routes.py`, `BuyerWorkspaceRepository`, `OwnedResourceNotFound`, `test_fresh_postgres_migrates_to_head`, `SqlAlchemyCatalogueRepository`, `contracts.py`, `AuthenticatedBuyer`, `test_media_api.py`, `test_auth.py`, `test_api.py`, `buyer_sql_repository.py`, `ListingQuery`, `FakeBuyerRepository`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `create_engine()` connect `test_fresh_postgres_migrates_to_head` to `test_buyer_repository.py`, `beat.py`, `SqlAlchemyIngestionRepository`, `create_app`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `SqlAlchemyBuyerWorkspaceRepository` (e.g. with `buyer_repositories()` and `AnonymousWorkspaceMergeRequest`) actually correct?**
  _`SqlAlchemyBuyerWorkspaceRepository` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `SqlAlchemyIngestionRepository` (e.g. with `CachedPhotoWrite` and `CrawlRunSummary`) actually correct?**
  _`SqlAlchemyIngestionRepository` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `create_app()` (e.g. with `AuthenticationError` and `AuthenticationUnavailableError`) actually correct?**
  _`create_app()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `BuyerWorkspaceRepository` (e.g. with `add_shortlist()` and `append_turn()`) actually correct?**
  _`BuyerWorkspaceRepository` has 23 INFERRED edges - model-reasoned connections that need verification._