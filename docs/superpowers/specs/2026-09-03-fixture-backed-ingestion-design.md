# Fixture-Backed Ingestion Vertical Slice Design

## Status

Approved for implementation planning on 3 September 2026.

## Objective

Build Carveo's first production-shaped ingestion workflow without contacting a live marketplace. The workflow must discover marketplace-shaped HTML fixtures, extract and normalize Source Listings through the existing Crawl4AI container, persist catalogue and media changes, reconcile disappearance, and expose real operational telemetry.

This milestone proves the ingestion architecture and data lifecycle. It does not make Carveo production-ready and does not authorize live crawling.

## Scope

### Included

- A Carveo-owned Fixture Source served as HTML over the private Docker network.
- Search-page discovery and detail-page extraction.
- English and Arabic fixture content.
- Deterministic JSON-LD extraction with CSS fallback.
- Pydantic validation and explicit rejected-record handling.
- Source authorization and environment gating before any fetch.
- Dramatiq tasks, Redis idempotency, bounded retries, and dead-letter behavior.
- Hourly scheduling through Beat and an on-demand development command.
- PostgreSQL crawl-run, run-item, extraction, lifecycle, price-history, and media metadata.
- MinIO-backed local image caching behind Carveo media URLs.
- Missing, removed, restored, and source-sold lifecycle handling.
- Prometheus metrics, structured logs, and Grafana ingestion panels.
- Unit, integration, worker, migration, contract, and end-to-end tests.

### Excluded

- Live Dubizzle or other marketplace traffic.
- Downloading marketplace pages to create fixtures without documented authorization.
- AI extraction, LangGraph, RAG, embeddings, reranking, or OpenRouter calls.
- Cross-source canonical vehicle grouping.
- Additional UAE sources or GCC markets.
- AWS, Vercel, Terraform/OpenTofu, CI deployment, or remote hosting implementation.
- Public administration screens or source-management controls.

Remote hosting remains the final future project milestone after the application is deployment-ready. The frontend will eventually deploy to Vercel; backend hosting will be designed separately when that milestone begins.

## Architectural Shape

The ingestion worker remains a separate runtime from FastAPI and Next.js. Dramatiq workers coordinate Ingestion Runs and write through repositories in `carveo-core`. The existing authenticated Crawl4AI v0.9.2 container owns browser execution. A private fixture-origin container serves Carveo-owned HTML so the same HTTP and browser path used by a future approved Source is exercised locally.

The main modules are:

1. **Source policy module**: loads a Source profile and decides whether a fetch is permitted for the current environment and URL.
2. **Source adapter module**: discovers listing references, requests rendered pages, and extracts source-shaped records.
3. **Normalization module**: converts source-shaped values into validated Carveo contracts without guessing missing facts.
4. **Ingestion coordinator module**: owns run state, idempotency, per-item processing, completion, and reconciliation.
5. **Catalogue writer module**: atomically creates or updates Source Listings and appends price observations only when price changes.
6. **Media cache module**: downloads every current image set, stores content-addressed objects, and atomically updates listing media metadata.
7. **Lifecycle module**: marks unseen listings missing, removes them after the threshold, restores them when seen again, and purges expired records.

Each module must have a small typed interface. Crawl4AI, PostgreSQL, Redis, the fixture origin, and MinIO are adapters at those interfaces. Tests use in-memory or stub adapters only where a second implementation genuinely exists; PostgreSQL-specific behavior remains covered by PostgreSQL integration tests.

## Source Policy

The existing `sources` record becomes an enforced gate. A Source profile contains:

- Stable source key and market.
- Authorization status: `fixture`, `pending`, `approved`, or `blocked`.
- Enabled flag and environment allowlist.
- Allowed domains and URL schemes.
- Terms-review timestamp.
- Adapter and parser versions.
- Per-source concurrency and request-rate ceilings.
- Kill-switch reason and timestamp when disabled.

The Fixture Source is authorized only in `development` and `test`. Its allowed host is the private fixture-origin container. Production mode rejects it. A pending, blocked, disabled, unreviewed, wrong-environment, wrong-domain, or wrong-scheme Source fails before Crawl4AI receives a request.

No code path may accept an arbitrary URL from a buyer, HTTP request, queue message, or saved search. Queue messages contain source keys and internal run identifiers, never unrestricted crawl targets.

## Fixture Corpus

The repository will contain synthetic HTML authored for Carveo. Fixtures must not copy marketplace branding, text, or markup verbatim. The corpus includes:

- Two search-result pages with pagination and duplicate discovery across pages.
- At least twelve listing-detail pages spanning several makes and body types.
- English-only, Arabic-only, and mixed-language listings.
- JSON-LD-first and CSS-fallback pages.
- Missing mileage, price, trim, condition evidence, and image cases.
- Explicit sold state.
- Changed price and changed image-set revisions.
- A listing absent from later search snapshots.
- A removed listing that returns before purge.
- Malformed JSON-LD, unsupported units, blocked response, timeout, and not-found fixtures.

Fixture revisions are immutable and versioned. Scenario manifests select which search and detail revisions an Ingestion Run sees. This allows repeatable lifecycle tests without editing fixture files between runs.

## Ingestion Contracts

The shared package defines validated contracts for:

- `SourceProfile`
- `SourceQuery`
- `ListingReference`
- `RawListing`
- `NormalizedListing`
- `NormalizedPhoto`
- `RejectedListing`
- `CrawlRunSummary`
- `CrawlRunItemResult`
- `MediaCacheResult`

`ListingReference` carries the Source key, source listing identifier when present, canonicalized URL, discovery timestamp, and originating search-page identity. `RawListing` preserves source text and extraction evidence. `NormalizedListing` contains typed Carveo values while retaining original text for every transformed value that may need audit.

Arabic titles and descriptions remain Arabic. Make, model, trim, city, units, currency, and regional specification may receive normalized companion values, but source text is never overwritten.

## Crawl4AI Adapter

The worker calls the existing authenticated Crawl4AI container through a typed client. The client owns authentication, request serialization, timeout policy, response validation, and error classification. It uses bounded, non-streaming requests.

The Fixture Source adapter separates four operations:

1. Build permitted fixture-origin search URLs from an internal `SourceQuery`.
2. Discover and deduplicate `ListingReference` values from rendered search pages.
3. Fetch rendered detail pages in bounded batches.
4. Extract `RawListing` values using JSON-LD first and versioned CSS selectors second.

Crawl4AI failures are classified as timeout, blocked, unavailable, invalid response, navigation failure, or unsupported content. Parser failures are separate from fetch failures. Neither class is silently converted into an empty discovery result.

## Persistence Model

### Existing records

`sources`, `listings`, `listing_photos`, `condition_evidence`, and `price_observations` remain the catalogue foundation.

### Source extensions

Add policy metadata for environment allowlisting, allowed hosts, parser version, concurrency, kill-switch state, and rate ceilings. Mutable operational policy must be changeable without rebuilding an image.

### Crawl runs

`crawl_runs` records:

- Source, trigger, correlation identifier, adapter version, and parser version.
- Queued, running, completed, partially completed, or failed status.
- Start and finish timestamps.
- Whether discovery completed successfully.
- Discovery, fetched, normalized, rejected, created, updated, unchanged, missing, removed, restored, and media counters.
- Sanitized terminal error category.

Detailed crawl-run and crawl-run-item records are retained for 90 days, then hard-deleted. Long-term operational trends live only in Prometheus-compatible aggregate metrics and contain no listing payloads or source URLs.

### Crawl-run items

`crawl_run_items` records one discovered reference per run with a uniqueness constraint on run and canonical source identity. It tracks fetch status, parse status, attempt count, content fingerprint, normalized listing identity, and sanitized failure category.

### Extraction artifacts

`extraction_artifacts` stores structured extraction payloads, evidence, parser version, content fingerprint, and purge timestamp. It does not persist arbitrary response headers, cookies, authentication material, or browser storage. Artifacts are hard-deleted after seven days.

### Listing lifecycle extensions

Listings gain missing timestamp, consecutive successful miss count, removed timestamp, source-sold timestamp, restored timestamp, and purge timestamp. Lifecycle status remains explicit and indexed.

### Retained market price observations

Price history is stored as an immutable market observation rather than depending solely on a live listing foreign key. Each observation snapshots only the normalized fields required for aggregate market analysis: market, make, model, model year, regional specification, mileage band, price, currency, and observation timestamp. While a listing exists, the observation may reference it for product features.

When a removed listing reaches its purge date, the listing link and source-specific identity are erased from retained observations. Source listing IDs, canonical URLs, seller identity, media, descriptions, and condition evidence are never retained in this anonymized history. This preserves long-term pricing analysis while honoring the seven-day deletion rule for the listing record and its images.

### Media metadata

Listing photos retain source URL provenance and gain storage key, content hash, media type, byte size, refreshed timestamp, and purge timestamp. Public catalogue contracts expose a Carveo media URL rather than the MinIO object URL.

## Identity and Deduplication

Within this milestone, identity is `Source + source listing ID`. When a fixture intentionally omits the identifier, an exact canonical source URL may be used only when it maps to one existing Source Listing. Ambiguous fallback matches are rejected for review rather than merged.

Repeated discovery within or across fixture search pages creates one crawl-run item. Repeated Ingestion Runs update the same Source Listing. Cross-source deduplication and canonical vehicle identity remain deferred until a second approved Source exists.

## Transaction and Completion Rules

An Ingestion Run is not one database transaction. Each Source Listing is persisted atomically so one malformed record cannot roll back successful records or hold a transaction across browser work.

Run completion and disappearance reconciliation follow stricter rules:

- Reconciliation runs only after every configured search page was discovered successfully.
- A failed or incomplete discovery phase never increments listing miss counts.
- Detail-page failures affect the run item but do not make that listing missing when its reference was discovered.
- Run counters and terminal status are finalized in one transaction.
- A process crash leaves the run recoverable as stale rather than completed.

## Listing Lifecycle and Retention

On a complete successful discovery:

- A discovered listing becomes or remains `active`.
- A previously missing or removed listing discovered before purge becomes `restored`, then active, with its prior identity and history retained.
- An undiscovered active listing becomes `missing` with miss count one.
- Each subsequent complete successful miss increments the count.
- The third consecutive successful miss makes the listing `removed` and assigns a purge timestamp seven days later.
- An explicit source-sold marker sets `source_sold_at` immediately and makes the listing unavailable without pretending disappearance proved a sale.
- Failed and partial runs do not advance absence state.

Seven days after removal, the purge task hard-deletes the listing record and cached images. It also deletes condition evidence, listing photos, source-specific extraction artifacts, source URLs, seller details, and listing-specific run-item links. Buyer shortlist and comparison references are removed by database constraints or explicit cleanup in the same transaction. Price observations survive only after their listing link and source-specific identity have been erased as defined above.

## Catalogue Updates

A normalized listing upsert distinguishes created, changed, and unchanged outcomes. It updates `last_seen_at` on every successful detail refresh. `first_seen_at` never changes.

A new immutable market price observation is appended only when the normalized price or currency differs from the latest observation. Other field changes update the listing and extraction audit metadata without manufacturing price history. Purging a listing anonymizes its retained observations; it does not erase the market-level price history.

Missing source evidence remains unknown. Extraction never infers accident-free status, service history, warranty, seller trust, or inspection state.

## Media Cache

Docker Compose adds MinIO and a one-shot bucket-initialization container. The worker accesses MinIO through an S3-compatible storage adapter. Bucket credentials remain in environment-backed secrets and are never exposed to the browser.

Every successful listing refresh attempts to refresh its current image set. The media module:

- Validates scheme, host, media type, declared and streamed size, and redirect destination.
- Downloads with bounded concurrency and byte limits.
- Computes a content hash and reuses identical objects.
- Writes new objects before changing listing-photo rows.
- Atomically swaps the listing's ordered image set after a successful refresh.
- Retains the last confirmed image set when a refresh fails and records the failure.
- Removes unreferenced objects during retention cleanup.

The catalogue exposes stable Carveo media routes. In local development FastAPI streams or redirects through a controlled media endpoint without exposing MinIO credentials or internal hostnames.

## Queueing, Idempotency, and Scheduling

Dramatiq owns tasks for starting a run, discovering pages, processing run items, finalizing reconciliation, refreshing media, and purging expired data. Task arguments are JSON-safe identifiers only.

A Redis idempotency key combines Source, query identity, fixture scenario, and hourly window. Concurrent requests for the same run collapse to one active run. Locks use bounded TTLs and database uniqueness remains the final duplicate defense.

Retries apply only to classified transient failures. Backoff is exponential with jitter and a fixed maximum attempt count. Permanent policy, validation, unsupported-content, and blocked-source failures do not retry automatically. Exhausted tasks retain a crawl-run item failure and follow the existing dead-letter path.

Beat enqueues hourly Fixture Source refreshes in local integrated development. Automated tests disable the scheduler. An on-demand development command accepts a fixture scenario and SourceQuery, enqueues the same task path, prints the run identifier, and can optionally wait for terminal status.

## Observability

All worker logs are structured JSON and include run ID, task message ID, Source key, run-item ID, source listing identity when known, adapter version, parser version, outcome, duration, and sanitized error category. Logs never include raw HTML, source credentials, cookies, authorization headers, or full image query strings.

Prometheus metrics cover:

- Run totals and durations by Source, trigger, and outcome.
- Discovery, fetch, parse, normalization, persistence, lifecycle, and media outcomes.
- Retry and dead-letter counts.
- Active-run age and stale-run count.
- Crawl4AI request latency and classified failures.
- Redis queue health.
- Listings created, updated, unchanged, missing, removed, restored, and purged.

Grafana adds an ingestion overview with run throughput, success ratio, stage failures, listing changes, media outcomes, stale runs, and queue health. Alerts cover no successful run within the expected window, sustained extraction rejection, Crawl4AI unavailability, stale active runs, dead letters, and purge failures.

## Failure Handling

- Source-policy rejection terminates before network work and records a policy failure.
- Crawl4AI unavailability retries within bounds and never produces disappearance reconciliation.
- Search-page parse failure makes discovery incomplete and prevents reconciliation.
- Detail-page parse failure rejects that run item while preserving the prior active listing.
- Database failure rolls back only the affected persistence transaction and retries when safe.
- Media failure preserves the last confirmed image set.
- Worker interruption leaves resumable run items and a stale run detectable by monitoring.
- Kill-switch activation prevents new work and causes queued work to stop at the policy gate.

## Integration with the Existing Application

The existing public catalogue remains the only buyer-facing read path. Ingestion writes the tables already read by `SqlAlchemyCatalogueRepository`, so created and updated fixture listings appear in the current Next.js routes without a parallel data store.

Generated OpenAPI contracts change only if media or operational responses require public contract changes. Browser-local and authenticated buyer workspaces continue to reference listing public IDs. Purge behavior must clean those references without exposing deleted listings.

No buyer action can trigger an unrestricted URL fetch. Saved searches may become refresh priorities in a later milestone, but Option A schedules only approved internal Fixture Source queries.

## Testing Strategy

### Unit tests

- Source-policy matrix across authorization, environment, enabled state, domain, and scheme.
- URL canonicalization and guarded identity fallback.
- JSON-LD precedence and CSS fallback.
- Arabic text preservation and normalized companion values.
- Unknown evidence handling and malformed record rejection.
- Lifecycle transitions, successful-run counting, restoration, source-sold state, and seven-day purge eligibility.
- Price-observation change detection.
- Media validation and content-hash reuse.
- Error classification and retry decisions.

### PostgreSQL integration tests

- Migrations apply from an empty database.
- Run and run-item uniqueness constraints enforce idempotency.
- Per-listing upserts are atomic.
- Incomplete discovery cannot advance miss counts.
- Three successful misses remove a listing.
- Restoration preserves identity and history before purge.
- Seven-day purge deletes listing records, images, and buyer references without orphans.
- Concurrent finalization cannot reconcile twice.

### Worker tests

- Dramatiq stub-broker task flow from run creation through finalization.
- Redis integration for enqueue deduplication, retry exhaustion, and dead letters.
- Crawl4AI client authentication, timeout, and response validation through an HTTP test adapter.
- Scheduler enqueues one run per Source/query/hour window.
- On-demand command uses the same coordinator path as Beat.

### Container integration tests

- Fixture origin, Crawl4AI, MinIO, Redis, PostgreSQL, worker, Beat, FastAPI, and Next.js become healthy.
- An initial scenario creates listings visible through the catalogue and frontend.
- A second scenario changes a price and image set without creating a duplicate listing.
- Three complete missing scenarios remove a listing.
- A restoration scenario reactivates it before the seven-day purge deadline.
- Prometheus scrapes ingestion metrics and Grafana provisions the ingestion dashboard.

### Security tests

- Arbitrary URLs, public hosts, file URLs, loopback aliases, redirects to disallowed hosts, and private-network targets outside the fixture allowlist are rejected.
- Oversized HTML, extraction payloads, images, and decompression responses are bounded.
- Crawl4AI and MinIO credentials never appear in public responses or logs.
- Production mode cannot enable the Fixture Source.

## Delivery Slices

1. Domain contracts, source policy, and migrations.
2. Fixture corpus and private fixture-origin container.
3. Typed Crawl4AI client and deterministic Fixture Source adapter.
4. Ingestion coordinator, repositories, run items, and listing upserts.
5. Lifecycle reconciliation, restoration, and seven-day purge.
6. MinIO media cache and Carveo media route.
7. Dramatiq orchestration, Redis idempotency, hourly Beat scheduling, and on-demand command.
8. Prometheus metrics, Grafana dashboard, alerts, and structured logs.
9. Full container journey, contract verification, documentation, and operational runbook.

Each slice must be independently testable and committed separately. Implementation follows test-first development and does not advance to live Source work when Option A acceptance fails.

## Acceptance Criteria

Option A is complete only when all of the following are demonstrated from a fresh environment:

1. Docker Compose starts every required container and all readiness checks pass.
2. An on-demand fixture Ingestion Run reaches a terminal successful state.
3. Synthetic English and Arabic Source Listings appear in PostgreSQL, the public catalogue, and the existing frontend.
4. A repeated identical run is idempotent and reports unchanged listings.
5. A changed fixture creates one price observation and atomically replaces the image set.
6. A failed or incomplete discovery does not mark listings missing.
7. Three consecutive complete successful misses remove a listing.
8. A listing restored before purge retains its public identity and history.
9. Removed listing records and cached images are hard-deleted seven days after removal, including buyer references.
10. Price observations survive listing purge only as anonymized market records with no listing, source, seller, URL, or media identity.
11. Crawl-run detail is purged after 90 days while aggregate operational metrics remain available.
12. Crawl4AI, source policy, retries, dead letters, and the kill switch are covered by automated tests.
13. Grafana displays real ingestion metrics collected by Prometheus.
14. Backend tests, linting, typing, migrations, frontend contract checks, frontend tests, production build, and the integrated browser journey pass.

## Future Gates

After Option A, the project may separately design an approved live Source milestone. That milestone requires a documented access decision before any live host is enabled. AI retrieval and recommendation work follows proven catalogue quality. Vercel and AWS hosting remain the final deployment milestone and are not part of this design.
