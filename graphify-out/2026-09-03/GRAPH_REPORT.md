# Graph Report - Carveo  (2026-09-03)

## Corpus Check
- 191 files · ~241,843 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1426 nodes · 2738 edges · 100 communities (80 shown, 20 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 279 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e897e3aa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- contracts.py
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
- BuyerWorkspaceClient
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
- buyer-workspace-client.test.ts
- FakeBuyerRepository
- Crawl4AIClient
- create_app
- buyer_routes.py
- BuyerWorkspaceRepository
- ListingQuery
- test_fresh_postgres_migrates_to_head
- File Structure
- Issue tracker: GitHub
- CONTEXT-MAP.md
- domain.md
- triage-labels.md
- api.ts
- fixture-catalogue-repository.ts
- en-ae/layout.tsx
- ingestion_contracts.py
- Settings
- api-catalogue-repository.ts
- condition-evidence.tsx
- test_contract.py
- OwnedResourceNotFound
- FixtureSourceAdapter
- SourcePolicy
- test_identity.py
- Ingestion
- test_auth.py
- comparison-workspace.tsx
- fixture.py
- fixture-catalogue.ts
- test_fixture_adapter.py
- test_models.py
- ClerkRequestAuthenticator
- test_buyer_api.py
- buyer_api
- WorkerSettings

## God Nodes (most connected - your core abstractions)
1. `SqlAlchemyBuyerWorkspaceRepository` - 50 edges
2. `BuyerWorkspaceRepository` - 36 edges
3. `FakeBuyerRepository` - 33 edges
4. `create_app()` - 32 edges
5. `FixtureCatalogueRepository` - 24 edges
6. `AuthenticatedBuyer` - 23 edges
7. `Fixture-Backed Ingestion Vertical Slice Design` - 23 edges
8. `FixtureSourceAdapter` - 20 edges
9. `Listing` - 20 edges
10. `ListingReference` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_buyer_contracts_reject_non_utc_timestamps()` --uses--> `ConversationTurn`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_buyer_workspace_rejects_duplicate_comparison_listing_ids()` --uses--> `BuyerWorkspace`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_buyer_workspace_rejects_more_than_four_comparison_listing_ids()` --uses--> `BuyerWorkspace`  [INFERRED]
  backend/packages/carveo-core/tests/test_models.py → backend/packages/carveo-core/src/carveo_core/buyer_contracts.py
- `test_source_profile_bounds_operational_limits()` --uses--> `SourceProfile`  [INFERRED]
  backend/packages/carveo-core/tests/test_ingestion_contracts.py → backend/packages/carveo-core/src/carveo_core/ingestion_contracts.py
- `test_queue_facing_source_query_contains_no_url()` --uses--> `SourceQuery`  [INFERRED]
  backend/packages/carveo-core/tests/test_ingestion_contracts.py → backend/packages/carveo-core/src/carveo_core/ingestion_contracts.py

## Import Cycles
- None detected.

## Communities (100 total, 20 thin omitted)

### Community 0 - "contracts.py"
Cohesion: 0.06
Nodes (63): client(), anyio, AsyncClient, fixture, ready(), test_detail_compare_and_missing_problem(), test_health_and_readiness_are_distinct(), test_invalid_range_is_problem_response() (+55 more)

### Community 1 - "Fixture-Backed Ingestion Vertical Slice Design"
Cohesion: 0.05
Nodes (38): Acceptance Criteria, Architectural Shape, Catalogue Updates, Container integration tests, Crawl4AI Adapter, Crawl-run items, Crawl runs, Delivery Slices (+30 more)

### Community 2 - "assistant-workspace.tsx"
Cohesion: 0.06
Nodes (42): ListingPage(), metadata, metadata, AppHeader(), AssistantWorkspace(), intentHref(), newId(), profile (+34 more)

### Community 3 - "devDependencies"
Cohesion: 0.04
Nodes (46): @axe-core/playwright, devDependencies, @axe-core/playwright, jsdom, openapi-typescript, @playwright/test, tailwindcss, @tailwindcss/postcss (+38 more)

### Community 4 - "query.ts"
Cohesion: 0.20
Nodes (11): CarsPage(), toParams(), bodyTypes, HomePage(), makeLinks, arrayKeys, numberKeys, parseListingQuery() (+3 more)

### Community 5 - "database.py"
Cohesion: 0.21
Nodes (10): do_run_migrations(), run_async_migrations(), run(), get_settings(), create_engine(), create_session_factory(), async_sessionmaker, AsyncEngine (+2 more)

### Community 6 - "profile-provider.tsx"
Cohesion: 0.20
Nodes (18): BrowserProfile, addComparison(), createEmptyProfile(), migrateProfile(), PROFILE_STORAGE_KEY, recordRecentView(), removeComparison(), saveSearchDraft() (+10 more)

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

### Community 13 - "BuyerWorkspaceClient"
Cohesion: 0.21
Nodes (4): BuyerWorkspace, Conversation, SavedSearch, BuyerWorkspaceClient

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
Cohesion: 0.07
Nodes (53): ValueError, _canonical_query(), _conversation_summary(), AsyncSession, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary (+45 more)

### Community 39 - "test_fixture_corpus.py"
Cohesion: 0.39
Nodes (5): load_manifest(), test_baseline_contains_twelve_unique_listings_and_a_cross_page_duplicate(), test_every_manifest_page_exists_and_uses_private_fixture_origin(), test_failure_scenario_covers_expected_failure_classes(), test_manifest_defines_immutable_lifecycle_scenarios()

### Community 40 - "Listing"
Cohesion: 0.28
Nodes (5): loadComparisonListings(), ComparePage(), Listing, ListingPage, CatalogueRepository

### Community 41 - "Global Constraints"
Cohesion: 0.18
Nodes (10): Authenticated Buyer Workspace Implementation Plan, Global Constraints, Task 1: Clerk Request Authentication Boundary, Task 2: Buyer Contracts, Tables, and Migration, Task 3: SQLAlchemy Buyer Workspace Repository, Task 4: Protected FastAPI Buyer Routes, Task 5: OpenAPI and TypeScript Buyer Contracts, Task 6: Authenticated Frontend Workspace Client (+2 more)

### Community 42 - "schemas.ts"
Cohesion: 0.10
Nodes (24): AnonymousConversation, anonymousConversationSchema, AssistantTurn, assistantTurnSchema, buyerWorkspaceSchema, ComparisonSelection, conversationSchema, ConversationSummary (+16 more)

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
Cohesion: 0.21
Nodes (23): AnonymousWorkspaceMergeRequest, BuyerContractModel, BuyerWorkspace, ComparisonUpdate, Conversation, ConversationCreate, ConversationSummary, ConversationTurn (+15 more)

### Community 62 - "buyer-workspace-client.test.ts"
Cohesion: 0.33
Nodes (3): emptyWorkspace, toAnonymousMergePayload(), WorkspaceRequestError

### Community 63 - "FakeBuyerRepository"
Cohesion: 0.17
Nodes (10): FakeBuyerRepository, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, SavedSearch, SavedSearchUpsert (+2 more)

### Community 64 - "Crawl4AIClient"
Cohesion: 0.14
Nodes (14): Crawl4AIClient, CrawlDocument, AsyncClient, BaseModel, crawl_result(), parametrize, Response, test_client_authenticates_uses_non_streaming_batches_and_preserves_order() (+6 more)

### Community 65 - "create_app"
Cohesion: 0.16
Nodes (18): AuthenticationError, AuthenticationUnavailableError, Exception, Protocol, RequestAuthenticator, configure_logging(), create_app(), listing_query() (+10 more)

### Community 66 - "buyer_routes.py"
Cohesion: 0.14
Nodes (29): AuthenticatedBuyer, add_shortlist(), append_turn(), buyer_repositories(), conversation_detail(), conversations(), create_conversation(), delete_saved_search() (+21 more)

### Community 67 - "BuyerWorkspaceRepository"
Cohesion: 0.12
Nodes (11): BuyerWorkspaceRepository, BuyerWorkspace, Conversation, ConversationCreate, ConversationSummary, ConversationTurnCreate, Protocol, SavedSearch (+3 more)

### Community 68 - "ListingQuery"
Cohesion: 0.47
Nodes (4): FilterFields(), options, MobileFilterDrawer(), ListingQuery

### Community 69 - "test_fresh_postgres_migrates_to_head"
Cohesion: 0.43
Nodes (7): _check_constraint_names(), _foreign_key_ondelete(), _foreign_key_targets(), _index_names(), test_fresh_postgres_migrates_to_head(), _unique_column_sets(), integration

### Community 70 - "File Structure"
Cohesion: 0.09
Nodes (21): Acceptance Checklist, API, observability, and frontend, File Structure, Fixture-Backed Ingestion Implementation Plan, Fixture origin and media, Global Constraints, Reference Notes, Shared backend domain (+13 more)

### Community 76 - "api.ts"
Cohesion: 0.33
Nodes (5): components, $defs, operations, paths, webhooks

### Community 77 - "fixture-catalogue-repository.ts"
Cohesion: 0.19
Nodes (6): DealPosition, ModelMarketSummary, calculateDealPosition(), median(), FixtureCatalogueRepository, matches()

### Community 79 - "ingestion_contracts.py"
Cohesion: 0.14
Nodes (22): CrawlRunItemResult, CrawlRunSummary, MediaCacheResult, NormalizedConditionEvidence, NormalizedListing, NormalizedPhoto, BaseModel, model_validator (+14 more)

### Community 80 - "Settings"
Cohesion: 0.29
Nodes (6): BaseSettings, model_validator, Settings, MonkeyPatch, test_production_requires_explicit_clerk_authorized_parties_and_a_verification_key(), test_settings_accept_clerk_cli_secret_without_copying_it()

### Community 82 - "api-catalogue-repository.ts"
Cohesion: 0.17
Nodes (6): ApiCatalogueRepository, listingPageSchema, modelSummarySchema, parseAllQuery(), CatalogueEnvironment, createCatalogueRepository()

### Community 83 - "condition-evidence.tsx"
Cohesion: 0.50
Nodes (3): ConditionEvidencePanel(), groups, ConditionEvidence

### Community 84 - "test_contract.py"
Cohesion: 0.33
Nodes (3): main(), test_committed_openapi_document_is_current(), Path

### Community 85 - "OwnedResourceNotFound"
Cohesion: 0.67
Nodes (3): OwnedResourceNotFound, A buyer-owned resource is absent or belongs to another buyer., LookupError

### Community 86 - "FixtureSourceAdapter"
Cohesion: 0.30
Nodes (9): ListingReference, RawListing, RejectedListing, SourceQuery, DiscoveryResult, BaseModel, Protocol, SourceAdapter (+1 more)

### Community 87 - "SourcePolicy"
Cohesion: 0.24
Nodes (12): SourceProfile, Any, ValueError, SourcePolicy, SourcePolicyError, profile_with(), parametrize, test_fixture_source_is_forbidden_in_production() (+4 more)

### Community 88 - "test_identity.py"
Cohesion: 0.24
Nodes (13): canonicalize_source_url(), ValueError, resolve_source_identity(), SourceIdentity, SourceIdentityError, parametrize, reference(), test_canonicalization_rejects_invalid_absolute_http_urls() (+5 more)

### Community 90 - "test_auth.py"
Cohesion: 0.14
Nodes (22): auth_client(), FakeAuthenticator, FakeClerkClient, FakeWorkspaceRepository, anyio, AsyncClient, BuyerWorkspace, Exception (+14 more)

### Community 91 - "comparison-workspace.tsx"
Cohesion: 0.23
Nodes (7): metadata, metadata, buildComparisonRows(), ComparisonRow, ComparisonWorkspace(), money(), catalogueRepository

### Community 92 - "fixture.py"
Cohesion: 0.18
Nodes (8): _additional_properties(), _brand_name(), _DetailParser, _find_vehicle(), _measurement(), _SearchParser, _text(), HTMLParser

### Community 93 - "fixture-catalogue.ts"
Cohesion: 0.15
Nodes (14): resolveModelSegment(), generateMetadata(), MarketPage(), resolveSegment(), MarketCharts(), fixtureCatalogue, mediaByBodyType, mediaByModel (+6 more)

### Community 94 - "test_fixture_adapter.py"
Cohesion: 0.50
Nodes (11): adapter(), FixtureFileClient, anyio, source_profile(), test_arabic_source_text_is_preserved_verbatim(), test_css_fallback_extracts_listing_when_json_ld_is_absent(), test_discovery_builds_manifest_urls_and_collapses_duplicate_source_identity(), test_failed_or_incomplete_search_page_never_reports_complete_discovery() (+3 more)

### Community 95 - "test_models.py"
Cohesion: 0.29
Nodes (9): _check_constraint_names(), _foreign_key_targets(), _index_names(), test_buyer_contracts_reject_non_utc_timestamps(), test_buyer_metadata_enforces_ownership_and_ordering_constraints(), test_buyer_workspace_rejects_duplicate_comparison_listing_ids(), test_buyer_workspace_rejects_more_than_four_comparison_listing_ids(), test_catalogue_metadata_contains_expected_tables() (+1 more)

### Community 96 - "ClerkRequestAuthenticator"
Cohesion: 0.25
Nodes (6): ClerkRequestAuthenticator, Request, require_buyer(), bearer_auth, HTTPAuthorizationCredentials, Security

### Community 97 - "test_buyer_api.py"
Cohesion: 0.56
Nodes (8): anyio, AsyncClient, test_conversation_routes_preserve_ownership_and_ordered_turn_contract(), test_public_routes_stay_public_and_cors_allows_authorization(), test_saved_search_routes_hide_foreign_ids_and_reject_empty_canonical_queries(), test_shortlist_and_comparison_routes_map_unknown_listings_and_validation(), test_workspace_and_merge_are_authenticated_and_camel_case(), verified()

### Community 98 - "buyer_api"
Cohesion: 0.40
Nodes (4): buyer_api(), FakeAuthenticator, fixture, Request

## Knowledge Gaps
- **416 isolated node(s):** `$schema`, `style`, `rsc`, `tsx`, `css` (+411 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_datetime()` connect `buyer_sql_repository.py` to `contracts.py`, `SqlAlchemyBuyerWorkspaceRepository`, `ingestion_contracts.py`, `SourcePolicy`, `fixture.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `create_app()` connect `create_app` to `ClerkRequestAuthenticator`, `contracts.py`, `buyer_api`, `BuyerWorkspaceRepository`, `database.py`, `SqlAlchemyBuyerWorkspaceRepository`, `OwnedResourceNotFound`, `test_auth.py`, `buyer_sql_repository.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `BuyerWorkspaceRepository` connect `BuyerWorkspaceRepository` to `create_app`, `buyer_routes.py`, `buyer_sql_repository.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `SqlAlchemyBuyerWorkspaceRepository` (e.g. with `buyer_repositories()` and `AnonymousWorkspaceMergeRequest`) actually correct?**
  _`SqlAlchemyBuyerWorkspaceRepository` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `BuyerWorkspaceRepository` (e.g. with `add_shortlist()` and `append_turn()`) actually correct?**
  _`BuyerWorkspaceRepository` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `FakeBuyerRepository` (e.g. with `AnonymousWorkspaceMergeRequest` and `BuyerWorkspace`) actually correct?**
  _`FakeBuyerRepository` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `create_app()` (e.g. with `AuthenticationError` and `AuthenticationUnavailableError`) actually correct?**
  _`create_app()` has 16 INFERRED edges - model-reasoned connections that need verification._