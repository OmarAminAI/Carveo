# Graph Report - Carveo  (2026-09-06)

## Corpus Check
- 212 files · ~255,089 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1758 nodes · 3892 edges · 120 communities (93 shown, 27 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 450 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9f76222b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- FixtureCatalogueRepository
- Fixture-Backed Ingestion Vertical Slice Design
- assistant-workspace.tsx
- devDependencies
- fixture-catalogue.ts
- FakeRepository
- profile-provider.tsx
- dependencies
- compilerOptions
- Carveo Buyer Search Refactor - Implementation Plan
- components.json
- Crawl4AI v0.9.2 vs Firecrawl - Research and Recommendation for the Used-Car AI Search App
- tasks.py
- [listingId]/page.tsx
- carveo-core
- anyio_backend
- route.ts
- app/layout.tsx
- carveo_api/__init__.py
- MediaCache
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
- Crawl4AIClient
- Path
- create_app
- button.tsx
- cars/page.tsx
- OwnedResourceNotFound
- File Structure
- Issue tracker: GitHub
- CONTEXT-MAP.md
- domain.md
- triage-labels.md
- IngestionCoordinator
- fixture-catalogue-repository.ts
- database.py
- carveo_api/media.py
- BuyerWorkspaceClient
- useProfile
- ListingReference
- BuyerWorkspaceRepository
- query.ts
- fixture.py
- app-header.tsx
- normalize_listing
- Ingestion
- test_auth.py
- comparison-workspace.tsx
- test_fixture_adapter.py
- catalogue-repository.ts
- scripts
- test_models.py
- test_ingestion_contracts.py
- package.json
- dependencies.py
- embla-carousel-react
- init.sh
- @fontsource/barlow-condensed
- lucide-react
- react
- recharts
- zod
- @types/react-dom
- .append_turn
- InvalidSavedSearchQueryError
- test_buyer_repository.py
- ClerkRequestAuthenticator
- test_media_api.py
- test_fresh_postgres_migrates_to_head
- Frontend UI Implementation Plan
- index.ts
- Frontend UI design discussion
- api.ts
- env.py

## God Nodes (most connected - your core abstractions)
1. `SqlAlchemyIngestionRepository` - 58 edges
2. `_datetime()` - 56 edges
3. `SqlAlchemyBuyerWorkspaceRepository` - 50 edges
4. `ListingReference` - 38 edges
5. `create_app()` - 37 edges
6. `BuyerWorkspaceRepository` - 36 edges
7. `FakeBuyerRepository` - 33 edges
8. `normalize_listing()` - 33 edges
9. `CrawlRunSummary` - 30 edges
10. `FakeRepository` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_buyer_workspace_rejects_duplicate_comparison_listing_ids()` --uses--> `BuyerWorkspace`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_buyer_workspace_rejects_more_than_four_comparison_listing_ids()` --uses--> `BuyerWorkspace`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_source_profile_bounds_operational_limits()` --uses--> `SourceProfile`  [INFERRED]
  backend/packages/carveo-core/tests/test_ingestion_contracts.py → backend/packages/carveo-core/src/carveo_core/ingestion_contracts.py
- `test_queue_facing_source_query_contains_no_url()` --uses--> `SourceQuery`  [INFERRED]
  backend/packages/carveo-core/tests/test_ingestion_contracts.py → backend/packages/carveo-core/src/carveo_core/ingestion_contracts.py
- `test_catalogue_metadata_contains_expected_tables()` --uses--> `Base`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/models.py

## Import Cycles
- None detected.

## Communities (120 total, 27 thin omitted)

### Community 0 - "FixtureCatalogueRepository"
Cohesion: 0.06
Nodes (63): client(), anyio, AsyncClient, fixture, ready(), test_detail_compare_and_missing_problem(), test_health_and_readiness_are_distinct(), test_invalid_range_is_problem_response() (+55 more)

### Community 1 - "Fixture-Backed Ingestion Vertical Slice Design"
Cohesion: 0.05
Nodes (38): Acceptance Criteria, Architectural Shape, Catalogue Updates, Container integration tests, Crawl4AI Adapter, Crawl-run items, Crawl runs, Delivery Slices (+30 more)

### Community 2 - "assistant-workspace.tsx"
Cohesion: 0.16
Nodes (16): metadata, AssistantWorkspace(), intentHref(), newId(), profile, Badge(), Bubble(), Marker() (+8 more)

### Community 3 - "devDependencies"
Cohesion: 0.07
Nodes (29): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+21 more)

### Community 4 - "fixture-catalogue.ts"
Cohesion: 0.18
Nodes (9): MarketCharts(), fixtureCatalogue, mediaByBodyType, mediaByModel, Seed, seeds, seedSchema, conditionEvidenceSchema (+1 more)

### Community 5 - "FakeRepository"
Cohesion: 0.14
Nodes (19): RunStatus, DiscoveryResult, BaseModel, coordinator(), FakeAdapter, FakeRepository, UUID, reference() (+11 more)

### Community 6 - "profile-provider.tsx"
Cohesion: 0.15
Nodes (22): AnonymousConversation, anonymousConversationSchema, BrowserProfile, addComparison(), createEmptyProfile(), migrateProfile(), PROFILE_STORAGE_KEY, recordRecentView() (+14 more)

### Community 7 - "dependencies"
Cohesion: 0.07
Nodes (27): @base-ui/react, class-variance-authority, @clerk/nextjs, @clerk/ui, clsx, dependencies, @base-ui/react, class-variance-authority (+19 more)

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

### Community 12 - "tasks.py"
Cohesion: 0.05
Nodes (52): actor, AsyncIOScheduler, BeatRuntime, BeatSettings, BeatStore, build_scheduler(), check(), is_fresh_heartbeat() (+44 more)

### Community 13 - "[listingId]/page.tsx"
Cohesion: 0.18
Nodes (7): ConditionEvidencePanel(), groups, PriceHistoryChart(), RecentViewRecorder(), VehicleGallery(), ConditionEvidence, PriceObservation

### Community 14 - "carveo-core"
Cohesion: 0.83
Nodes (4): carveo-api, carveo-core, carveo-worker, carveo-workspace

### Community 20 - "MediaCache"
Cohesion: 0.08
Nodes (33): MediaCacheResult, _DownloadedPhoto, _failed(), MediaCache, MediaValidationError, AsyncClient, UUID, ValueError (+25 more)

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
Cohesion: 0.13
Nodes (22): _conversation_summary(), AsyncSession, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, SavedSearch (+14 more)

### Community 39 - "test_fixture_corpus.py"
Cohesion: 0.39
Nodes (5): load_manifest(), test_baseline_contains_twelve_unique_listings_and_a_cross_page_duplicate(), test_every_manifest_page_exists_and_uses_private_fixture_origin(), test_failure_scenario_covers_expected_failure_classes(), test_manifest_defines_immutable_lifecycle_scenarios()

### Community 40 - "Listing"
Cohesion: 0.17
Nodes (7): Listing, ListingPage, ApiCatalogueRepository, listingPageSchema, modelSummarySchema, parseAllQuery(), CatalogueRepository

### Community 41 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Authenticated Buyer Workspace Implementation Plan, Global Constraints, Task 1: Clerk Request Authentication Boundary, Task 2: Buyer Contracts, Tables, and Migration, Task 3: SQLAlchemy Buyer Workspace Repository, Task 4: Protected FastAPI Buyer Routes, Task 5: OpenAPI and TypeScript Buyer Contracts, Task 6: Authenticated Frontend Workspace Client (+2 more)

### Community 42 - "schemas.ts"
Cohesion: 0.10
Nodes (23): AssistantTurn, assistantTurnSchema, buyerWorkspaceSchema, ComparisonSelection, conversationSchema, ConversationSummary, conversationSummarySchema, ConversationTurn (+15 more)

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
Cohesion: 0.27
Nodes (18): AnonymousWorkspaceMergeRequest, BuyerContractModel, BuyerWorkspace, ComparisonUpdate, Conversation, ConversationCreate, ConversationSummary, ConversationTurn (+10 more)

### Community 62 - "SqlAlchemyIngestionRepository"
Cohesion: 0.06
Nodes (74): _require_utc_datetime(), _datetime(), CachedPhotoWrite, CrawlRunSummary, model_validator, SourceQuery, CreateRun, IngestionModel (+66 more)

### Community 63 - "FakeBuyerRepository"
Cohesion: 0.12
Nodes (22): buyer_api(), FakeAuthenticator, FakeBuyerRepository, anyio, AsyncClient, BuyerWorkspace, Conversation, ConversationCreate (+14 more)

### Community 64 - "Crawl4AIClient"
Cohesion: 0.14
Nodes (14): Crawl4AIClient, CrawlDocument, AsyncClient, BaseModel, crawl_result(), parametrize, Response, test_client_authenticates_uses_non_streaming_batches_and_preserves_order() (+6 more)

### Community 65 - "Path"
Cohesion: 0.33
Nodes (3): main(), test_committed_openapi_document_is_current(), Path

### Community 66 - "create_app"
Cohesion: 0.16
Nodes (18): AuthenticationError, AuthenticationUnavailableError, Exception, Protocol, RequestAuthenticator, configure_logging(), create_app(), listing_query() (+10 more)

### Community 67 - "button.tsx"
Cohesion: 0.21
Nodes (7): EmptyState(), SearchConsole(), vehicleSuggestions, Button(), ButtonProps, buttonVariants, VehicleSummary()

### Community 68 - "cars/page.tsx"
Cohesion: 0.18
Nodes (16): metadata, BrowseLink(), BrowseNavigation(), BrowseResults(), BrowseSort(), FilterForm(), filterKeys, NavigationContext (+8 more)

### Community 69 - "OwnedResourceNotFound"
Cohesion: 0.67
Nodes (3): OwnedResourceNotFound, LookupError, A buyer-owned resource is absent or belongs to another buyer.

### Community 70 - "File Structure"
Cohesion: 0.09
Nodes (21): Acceptance Checklist, API, observability, and frontend, File Structure, Fixture-Backed Ingestion Implementation Plan, Fixture origin and media, Global Constraints, Reference Notes, Shared backend domain (+13 more)

### Community 76 - "IngestionCoordinator"
Cohesion: 0.12
Nodes (12): CrawlRunItemResult, NormalizedPhoto, Protocol, SourceAdapter, CoordinatorRepository, _identity_key(), IngestionCoordinator, MediaCachePort (+4 more)

### Community 77 - "fixture-catalogue-repository.ts"
Cohesion: 0.19
Nodes (6): DealPosition, ModelMarketSummary, calculateDealPosition(), median(), FixtureCatalogueRepository, matches()

### Community 78 - "database.py"
Cohesion: 0.16
Nodes (14): run(), get_settings(), BaseSettings, model_validator, Settings, MonkeyPatch, test_production_requires_explicit_clerk_authorized_parties_and_a_verification_key(), test_settings_accept_clerk_cli_secret_without_copying_it() (+6 more)

### Community 79 - "carveo_api/media.py"
Cohesion: 0.18
Nodes (9): DatabaseMediaService, MediaAsset, MediaService, ObjectReader, async_sessionmaker, AsyncSession, Protocol, UUID (+1 more)

### Community 80 - "BuyerWorkspaceClient"
Cohesion: 0.21
Nodes (4): BuyerWorkspace, Conversation, SavedSearch, BuyerWorkspaceClient

### Community 82 - "useProfile"
Cohesion: 0.20
Nodes (10): CompareButton(), CompareTray(), noListings, DealPosition(), ShortlistButton(), ShortlistWorkspace(), Tab, tabs (+2 more)

### Community 83 - "ListingReference"
Cohesion: 0.25
Nodes (12): ListingReference, NormalizedConditionEvidence, BaseModel, RawConditionClaim, RawListing, RawPhoto, RejectedListing, _require_utc() (+4 more)

### Community 84 - "BuyerWorkspaceRepository"
Cohesion: 0.10
Nodes (36): AuthenticatedBuyer, add_shortlist(), append_turn(), buyer_repositories(), conversation_detail(), conversations(), create_conversation(), delete_saved_search() (+28 more)

### Community 85 - "query.ts"
Cohesion: 0.21
Nodes (11): CarsPage(), toParams(), bodyTypes, HomePage(), makeLinks, arrayKeys, numberKeys, parseListingQuery() (+3 more)

### Community 86 - "fixture.py"
Cohesion: 0.17
Nodes (9): _additional_properties(), _brand_name(), _DetailParser, _find_vehicle(), _measurement(), Any, _SearchParser, _text() (+1 more)

### Community 87 - "app-header.tsx"
Cohesion: 0.24
Nodes (6): dynamic, AppFooter(), AppHeader(), AuthControls(), AuthControlsProps, MobileNavigation()

### Community 88 - "normalize_listing"
Cohesion: 0.10
Nodes (47): NormalizedListing, canonicalize_source_url(), ValueError, resolve_source_identity(), SourceIdentity, SourceIdentityError, _alias_key(), NormalizationError (+39 more)

### Community 90 - "test_auth.py"
Cohesion: 0.14
Nodes (22): auth_client(), FakeAuthenticator, FakeClerkClient, FakeWorkspaceRepository, anyio, AsyncClient, BuyerWorkspace, Exception (+14 more)

### Community 91 - "comparison-workspace.tsx"
Cohesion: 0.27
Nodes (7): loadComparisonListings(), ComparePage(), metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money()

### Community 92 - "test_fixture_adapter.py"
Cohesion: 0.50
Nodes (11): adapter(), FixtureFileClient, anyio, source_profile(), test_arabic_source_text_is_preserved_verbatim(), test_css_fallback_extracts_listing_when_json_ld_is_absent(), test_discovery_builds_manifest_urls_and_collapses_duplicate_source_identity(), test_failed_or_incomplete_search_page_never_reports_complete_discovery() (+3 more)

### Community 93 - "catalogue-repository.ts"
Cohesion: 0.42
Nodes (5): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), slugifyVehicleName()

### Community 94 - "scripts"
Cohesion: 0.18
Nodes (11): scripts, build, contracts:check, contracts:generate, dev, start, test, test:e2e (+3 more)

### Community 95 - "test_models.py"
Cohesion: 0.29
Nodes (9): _check_constraint_names(), _foreign_key_targets(), _index_names(), test_buyer_contracts_reject_non_utc_timestamps(), test_buyer_metadata_enforces_ownership_and_ordering_constraints(), test_buyer_workspace_rejects_duplicate_comparison_listing_ids(), test_buyer_workspace_rejects_more_than_four_comparison_listing_ids(), test_catalogue_metadata_contains_expected_tables() (+1 more)

### Community 96 - "test_ingestion_contracts.py"
Cohesion: 0.36
Nodes (8): _normalized_payload(), _reference(), test_contracts_reject_extra_fields_and_non_utc_timestamps(), test_ingestion_result_contracts_are_strict_and_json_safe(), test_normalized_listing_preserves_arabic_source_text(), test_queue_facing_source_query_contains_no_url(), test_raw_listing_accepts_missing_source_fields_for_later_rejection(), test_source_profile_bounds_operational_limits()

### Community 97 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 99 - "dependencies.py"
Cohesion: 0.19
Nodes (16): SourceProfile, build_coordinator(), _load_fixture_profile(), _utc_now(), BaseSettings, WorkerSettings, ValueError, SourcePolicy (+8 more)

### Community 108 - ".append_turn"
Cohesion: 0.29
Nodes (4): Conversation, ConversationCreate, ConversationTurnCreate, UUID

### Community 109 - "InvalidSavedSearchQueryError"
Cohesion: 0.33
Nodes (4): InvalidSavedSearchQueryError, ValueError, _canonical_query(), test_empty_canonical_saved_search_query_raises_domain_error_without_persisting()

### Community 110 - "test_buyer_repository.py"
Cohesion: 0.23
Nodes (16): anyio_backend(), _AsyncRendezvous, _clear_buyers(), postgres_database_url(), async_sessionmaker, AsyncSession, fixture, MonkeyPatch (+8 more)

### Community 112 - "ClerkRequestAuthenticator"
Cohesion: 0.25
Nodes (6): ClerkRequestAuthenticator, Request, require_buyer(), bearer_auth, HTTPAuthorizationCredentials, Security

### Community 113 - "test_media_api.py"
Cohesion: 0.28
Nodes (11): client(), anyio, AsyncClient, fixture, UUID, StubMediaService, test_media_openapi_contract_declares_binary_image_responses(), test_media_proxy_returns_bytes_type_etag_and_immutable_cache_headers() (+3 more)

### Community 114 - "test_fresh_postgres_migrates_to_head"
Cohesion: 0.43
Nodes (7): _check_constraint_names(), _foreign_key_ondelete(), _foreign_key_targets(), _index_names(), test_fresh_postgres_migrates_to_head(), _unique_column_sets(), integration

### Community 115 - "Frontend UI Implementation Plan"
Cohesion: 0.22
Nodes (8): Frontend UI Implementation Plan, Global constraints, Progress, Task 1: Responsive browsing and filters, Task 2: Vehicle presentation and persistent selection, Task 3: Comparison clarity, Task 4: Verification and review, Verification record — 2026-09-06

### Community 116 - "index.ts"
Cohesion: 0.32
Nodes (4): metadata, CatalogueEnvironment, catalogueRepository, createCatalogueRepository()

### Community 118 - "Frontend UI design discussion"
Cohesion: 0.33
Nodes (5): Agreed direction, Consolidated design, Documentation disposition, Frontend UI design discussion, Proposed acceptance checks

### Community 119 - "api.ts"
Cohesion: 0.33
Nodes (5): components, $defs, operations, paths, webhooks

## Knowledge Gaps
- **433 isolated node(s):** `init.sh script`, `$schema`, `style`, `rsc`, `tsx` (+428 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_datetime()` connect `SqlAlchemyIngestionRepository` to `FixtureCatalogueRepository`, `dependencies.py`, `FakeRepository`, `SqlAlchemyBuyerWorkspaceRepository`, `IngestionCoordinator`, `ListingReference`, `MediaCache`, `fixture.py`, `normalize_listing`, `buyer_sql_repository.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `create_app()` connect `create_app` to `FixtureCatalogueRepository`, `OwnedResourceNotFound`, `SqlAlchemyBuyerWorkspaceRepository`, `InvalidSavedSearchQueryError`, `database.py`, `carveo_api/media.py`, `ClerkRequestAuthenticator`, `test_media_api.py`, `BuyerWorkspaceRepository`, `test_auth.py`, `FakeBuyerRepository`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `build_coordinator()` connect `dependencies.py` to `Crawl4AIClient`, `Path`, `IngestionCoordinator`, `tasks.py`, `database.py`, `ListingReference`, `MediaCache`, `SqlAlchemyIngestionRepository`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `SqlAlchemyIngestionRepository` (e.g. with `CachedPhotoWrite` and `CrawlRunSummary`) actually correct?**
  _`SqlAlchemyIngestionRepository` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `SqlAlchemyBuyerWorkspaceRepository` (e.g. with `buyer_repositories()` and `AnonymousWorkspaceMergeRequest`) actually correct?**
  _`SqlAlchemyBuyerWorkspaceRepository` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ListingReference` (e.g. with `IngestionRepository` and `SqlAlchemyIngestionRepository`) actually correct?**
  _`ListingReference` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `create_app()` (e.g. with `AuthenticationError` and `AuthenticationUnavailableError`) actually correct?**
  _`create_app()` has 17 INFERRED edges - model-reasoned connections that need verification._