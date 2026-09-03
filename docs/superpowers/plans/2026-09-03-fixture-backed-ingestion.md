# Fixture-Backed Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a production-shaped, fixture-only Crawl4AI ingestion workflow that safely updates Carveo's PostgreSQL catalogue, caches media in MinIO, reconciles listing lifecycle, and exposes real operational telemetry.

**Architecture:** `carveo-core` owns validated ingestion contracts, PostgreSQL records, and transactional catalogue/lifecycle repositories. `carveo-worker` owns source policy, Crawl4AI HTTP access, deterministic extraction, normalization, orchestration, Dramatiq tasks, scheduling, media storage, and maintenance commands. FastAPI remains the buyer-facing read API and gains only stable Carveo media delivery; the existing Next.js catalogue consumes the same listing contract.

**Tech Stack:** Python 3.12, uv workspace, Pydantic v2, SQLAlchemy 2 async, PostgreSQL 18, Alembic, Dramatiq 2.2, Redis 8, HTTPX, Crawl4AI 0.9.2 Docker API, MinIO/S3, FastAPI, Prometheus, Grafana, Pytest/Testcontainers, Next.js 16, Bun, Zod, Playwright.

**Spec:** `docs/superpowers/specs/2026-09-03-fixture-backed-ingestion-design.md`

## Global Constraints

- This milestone uses only Carveo-authored synthetic fixtures. It must not contact Dubizzle or another live marketplace.
- Fixture Sources are allowed only in `development` and `test`; production rejects them before a network call.
- Queue messages contain source keys, query keys, scenario names, and internal UUIDs only; no arbitrary target URL enters through an API, buyer action, or queue message.
- Use authenticated, bounded, non-streaming `POST /crawl` requests to the existing `unclecode/crawl4ai:0.9.2` container.
- JSON-LD has extraction precedence; versioned CSS selectors are the deterministic fallback. No LLM extraction is permitted.
- Arabic listing titles and descriptions remain Arabic. Normalized companion values never overwrite source text.
- One complete successful absence marks a listing missing; three consecutive complete successful absences mark it removed. Failed or partial discovery never increments absence state.
- A removed listing and all cached images are hard-deleted seven days after removal.
- Price history survives listing deletion only as anonymized market observations with no listing, source, seller, URL, description, evidence, or media identity.
- Extraction artifacts are hard-deleted after seven days. Detailed run and run-item records are hard-deleted after 90 days.
- Public image values are stable Carveo URLs; MinIO credentials, bucket names, storage keys, and internal hostnames never reach the browser.
- Scheduler execution is disabled during automated tests. Local integrated development supports hourly runs and an explicit on-demand command.
- AWS, Vercel, Terraform/OpenTofu, live source access, AI/RAG, and cross-source vehicle grouping are outside this plan.
- Run backend commands from `backend/`; run frontend commands from `frontend/`.

---

## File Structure

### Shared backend domain

- `backend/packages/carveo-core/src/carveo_core/ingestion_contracts.py`: Pydantic contracts and enums shared by repositories and workers.
- `backend/packages/carveo-core/src/carveo_core/ingestion.py`: repository protocols, lifecycle decisions, and retry-independent domain rules.
- `backend/packages/carveo-core/src/carveo_core/ingestion_sql_repository.py`: PostgreSQL run, item, listing upsert, reconciliation, and purge transactions.
- `backend/packages/carveo-core/src/carveo_core/models.py`: ingestion records and catalogue lifecycle/media fields.
- `backend/apps/api/alembic/versions/20260903_0003_ingestion_foundation.py`: schema migration and buyer-reference deletion behavior.

### Worker

- `backend/workers/ingestion/src/carveo_worker/settings.py`: validated worker, Crawl4AI, source, scheduling, and S3 settings.
- `backend/workers/ingestion/src/carveo_worker/source_policy.py`: environment, authorization, scheme, host, and kill-switch gate.
- `backend/workers/ingestion/src/carveo_worker/identity.py`: URL canonicalization and guarded source identity fallback.
- `backend/workers/ingestion/src/carveo_worker/crawl4ai_client.py`: authenticated HTTP transport and failure classification.
- `backend/workers/ingestion/src/carveo_worker/adapters/base.py`: source adapter protocol.
- `backend/workers/ingestion/src/carveo_worker/adapters/fixture.py`: fixture URL construction, discovery, and deterministic extraction.
- `backend/workers/ingestion/src/carveo_worker/normalization.py`: source-shaped to catalogue-shaped normalization.
- `backend/workers/ingestion/src/carveo_worker/media.py`: safe download validation and cache coordination.
- `backend/workers/ingestion/src/carveo_worker/storage.py`: S3-compatible object storage protocol and MinIO adapter.
- `backend/workers/ingestion/src/carveo_worker/coordinator.py`: resumable run state machine.
- `backend/workers/ingestion/src/carveo_worker/tasks.py`: thin Dramatiq actors using JSON-safe identifiers.
- `backend/workers/ingestion/src/carveo_worker/beat.py`: health cycle plus hourly ingestion and maintenance scheduling.
- `backend/workers/ingestion/src/carveo_worker/cli.py`: on-demand fixture run command.
- `backend/workers/ingestion/src/carveo_worker/metrics.py`: bounded-label ingestion metrics.

### Fixture origin and media

- `backend/infra/fixtures/nginx.conf`: private static fixture-origin server configuration.
- `backend/infra/fixtures/site/scenarios.json`: immutable scenario-to-revision manifest.
- `backend/infra/fixtures/site/search/*.html`: synthetic paginated discovery pages.
- `backend/infra/fixtures/site/listings/*.html`: synthetic English, Arabic, mixed, malformed, sold, changed, and restored details.
- `backend/infra/fixtures/site/media/*`: Carveo-owned WebP fixture images.
- `backend/infra/minio/init.sh`: idempotent private bucket creation and lifecycle-independent setup.

### API, observability, and frontend

- `backend/apps/api/src/carveo_api/media.py`: validated Carveo media route and S3 streaming adapter.
- `backend/apps/api/src/carveo_api/main.py`: media router registration only.
- `backend/infra/observability/prometheus/{prometheus.yml,alerts.yml}`: ingestion scraping and alerts.
- `backend/infra/observability/grafana/dashboards/carveo-operations.json`: ingestion dashboard rows.
- `frontend/src/repositories/api-catalogue-repository.test.ts`: public media URL contract regression.
- `frontend/e2e/ingested-catalogue.spec.ts`: integrated fixture-ingestion buyer journey.

---

### Task 1: Define Ingestion Contracts and Database Schema

**Files:**
- Create: `backend/packages/carveo-core/src/carveo_core/ingestion_contracts.py`
- Modify: `backend/packages/carveo-core/src/carveo_core/models.py`
- Create: `backend/apps/api/alembic/versions/20260903_0003_ingestion_foundation.py`
- Modify: `backend/apps/api/tests/test_migrations.py`
- Create: `backend/packages/carveo-core/tests/test_ingestion_contracts.py`
- Modify: `backend/packages/carveo-core/tests/test_models.py`

**Interfaces:**
- Produces: `SourceProfile`, `SourceQuery`, `ListingReference`, `RawListing`, `NormalizedListing`, `NormalizedPhoto`, `RejectedListing`, `CrawlRunSummary`, `CrawlRunItemResult`, `MediaCacheResult`.
- Produces: `CrawlRunRecord`, `CrawlRunItemRecord`, `ExtractionArtifactRecord` and lifecycle/media extensions on existing records.
- Produces: nullable `PriceObservationRecord.listing_id` with anonymized market snapshot columns.

- [ ] **Step 1: Write contract validation tests**

```python
def test_normalized_listing_preserves_arabic_source_text() -> None:
    listing = NormalizedListing.model_validate(normalized_listing_payload(title="تويوتا راف فور"))
    assert listing.title == "تويوتا راف فور"
    assert listing.make == "Toyota"


def test_queue_facing_source_query_contains_no_url() -> None:
    assert "url" not in SourceQuery.model_fields
```

- [ ] **Step 2: Run the tests and confirm the contracts do not exist yet**

Run: `uv run pytest packages/carveo-core/tests/test_ingestion_contracts.py -q`

Expected: collection fails because `carveo_core.ingestion_contracts` is absent.

- [ ] **Step 3: Add strict contracts and enums**

```python
class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partially_completed"
    FAILED = "failed"


class SourceQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    market: Literal["ae"] = "ae"
    query_key: str = Field(min_length=1, max_length=120)
    fixture_scenario: str = Field(min_length=1, max_length=80)
```

Define all contracts named above with `extra="forbid"`, UTC-aware timestamps, non-negative prices/mileage, bounded confidence, and explicit literal values matching the approved design.

- [ ] **Step 4: Add migration assertions before the migration**

Extend `test_fresh_postgres_migrates_to_head` to assert the three new tables, source policy columns, listing lifecycle columns, photo storage columns, run/item uniqueness, lifecycle indexes, `ON DELETE SET NULL` for price observations, and `ON DELETE CASCADE` for buyer shortlist/comparison listing references.

- [ ] **Step 5: Run the migration test and confirm it fails**

Run: `uv run pytest apps/api/tests/test_migrations.py -q -m integration`

Expected: FAIL because revision `20260903_0003` and its tables are absent.

- [ ] **Step 6: Implement ORM records and Alembic migration**

Use explicit columns for run status and timestamps; store run counters in a non-null JSONB object. Add source policy fields (`environment_allowlist`, `allowed_hosts`, `allowed_schemes`, `parser_version`, `concurrency_limit`, `rate_limit_per_minute`, `killed_at`, `kill_reason`). Add listing lifecycle timestamps and miss count. Add photo storage metadata. Change buyer listing foreign keys to `ondelete="CASCADE"`.

For `price_observations`, use:

```python
listing_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("listings.id", ondelete="SET NULL"), nullable=True
)
market: Mapped[str] = mapped_column(String(8), nullable=False)
make: Mapped[str] = mapped_column(String(100), nullable=False)
model: Mapped[str] = mapped_column(String(100), nullable=False)
year: Mapped[int] = mapped_column(Integer, nullable=False)
specifications: Mapped[str] = mapped_column(String(48), nullable=False)
mileage_band_km: Mapped[int] = mapped_column(Integer, nullable=False)
currency: Mapped[str] = mapped_column(String(3), nullable=False)
```

Backfill snapshot columns from `listings` before applying non-null constraints.

- [ ] **Step 7: Verify schema and contracts**

Run: `uv run pytest packages/carveo-core/tests/test_ingestion_contracts.py packages/carveo-core/tests/test_models.py -q`

Run: `uv run pytest apps/api/tests/test_migrations.py -q -m integration`

Expected: all selected tests pass.

- [ ] **Step 8: Commit the schema boundary**

```bash
git add backend/packages/carveo-core backend/apps/api/alembic backend/apps/api/tests/test_migrations.py
git commit -m "feat: add ingestion domain and schema"
```

### Task 2: Build Source Policy and Identity Guards

**Files:**
- Create: `backend/workers/ingestion/src/carveo_worker/source_policy.py`
- Create: `backend/workers/ingestion/src/carveo_worker/identity.py`
- Create: `backend/workers/ingestion/tests/test_source_policy.py`
- Create: `backend/workers/ingestion/tests/test_identity.py`

**Interfaces:**
- Consumes: `SourceProfile`, `ListingReference` from Task 1.
- Produces: `SourcePolicy.authorize(profile, environment, url) -> None`.
- Produces: `canonicalize_source_url(url: str) -> str` and `resolve_source_identity(reference) -> SourceIdentity`.

`SourceIdentity` is a frozen dataclass with `source_key: str`, `source_listing_id: str | None`, and `canonical_url: str`. `resolve_source_identity` requires a source listing ID unless the caller supplies an exact canonical-URL lookup result containing exactly one existing listing ID.

- [ ] **Step 1: Write the complete policy matrix as parameterized tests**

```python
@pytest.mark.parametrize(
    ("change", "error_code"),
    [
        ({"enabled": False}, "source_disabled"),
        ({"authorization_status": "pending"}, "source_not_authorized"),
        ({"authorization_status": "blocked"}, "source_blocked"),
        ({"environment_allowlist": ["test"]}, "environment_not_allowed"),
        ({"killed_at": datetime.now(UTC)}, "source_killed"),
    ],
)
def test_policy_rejects_before_fetch(change: dict[str, object], error_code: str) -> None:
    with pytest.raises(SourcePolicyError, match=error_code):
        SourcePolicy().authorize(profile_with(**change), "development", FIXTURE_URL)
```

Also test wrong scheme, host, absent terms review, fixture-in-production, and the valid development/test matrix.

- [ ] **Step 2: Write canonicalization and guarded fallback tests**

Assert lowercase host, removed fragments, sorted query parameters, removed tracking parameters, retained semantic parameters, and rejection when a URL-only fallback matches zero or multiple records.

- [ ] **Step 3: Confirm both test modules fail**

Run: `uv run pytest workers/ingestion/tests/test_source_policy.py workers/ingestion/tests/test_identity.py -q`

Expected: import failures for both new modules.

- [ ] **Step 4: Implement the pure policy and identity modules**

```python
class SourcePolicy:
    def authorize(self, profile: SourceProfile, environment: str, url: str) -> None:
        parsed = urlsplit(url)
        if profile.authorization_status not in {"fixture", "approved"}:
            raise SourcePolicyError("source_not_authorized")
        if profile.authorization_status == "fixture" and environment == "production":
            raise SourcePolicyError("fixture_forbidden_in_production")
        if parsed.scheme not in profile.allowed_schemes or parsed.hostname not in profile.allowed_hosts:
            raise SourcePolicyError("target_not_allowed")
```

Keep every rejection deterministic and expose a bounded error code, not the rejected URL.

- [ ] **Step 5: Verify and commit**

Run: `uv run pytest workers/ingestion/tests/test_source_policy.py workers/ingestion/tests/test_identity.py -q`

```bash
git add backend/workers/ingestion/src/carveo_worker/source_policy.py backend/workers/ingestion/src/carveo_worker/identity.py backend/workers/ingestion/tests
git commit -m "feat: enforce ingestion source policy"
```

### Task 3: Add the Synthetic Fixture Origin

**Files:**
- Create: `backend/infra/fixtures/nginx.conf`
- Create: `backend/infra/fixtures/site/scenarios.json`
- Create: `backend/infra/fixtures/site/search/*.html`
- Create: `backend/infra/fixtures/site/listings/*.html`
- Create: `backend/infra/fixtures/site/media/*.webp`
- Create: `backend/workers/ingestion/tests/test_fixture_corpus.py`
- Modify: `backend/docker-compose.yml`

**Interfaces:**
- Produces: private origin `http://fixture-origin:8080` with `/health`, scenario search pages, detail pages, and media.
- Produces: immutable scenario names `baseline`, `unchanged`, `changed`, `missing-1`, `missing-2`, `removed`, `restored`, and `failures`.

- [ ] **Step 1: Write corpus integrity tests**

Load `scenarios.json` and assert every referenced file exists, every detail URL belongs to `fixture-origin`, at least 12 unique source IDs exist, pagination contains a deliberate duplicate, Arabic and mixed pages exist, and failure fixtures cover malformed JSON-LD, unsupported units, blocked, timeout, and not-found responses.

- [ ] **Step 2: Run the integrity test and confirm it fails**

Run: `uv run pytest workers/ingestion/tests/test_fixture_corpus.py -q`

Expected: FAIL because the manifest does not exist.

- [ ] **Step 3: Author the fixture corpus**

Use valid `Vehicle`/`Product` JSON-LD on primary pages and `data-carveo-*` selectors on fallback pages. Embed scenario revision identifiers in fixture-only metadata. Keep all copy, markup, and WebP assets Carveo-owned and synthetic.

- [ ] **Step 4: Add the private fixture-origin service**

```yaml
fixture-origin:
  image: nginx:1.29-alpine
  volumes:
    - ./infra/fixtures/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    - ./infra/fixtures/site:/usr/share/nginx/html:ro
  expose: ["8080"]
  healthcheck:
    test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/health"]
    interval: 5s
    timeout: 3s
    retries: 6
  logging: *default-logging
```

Do not publish the service to the host.

- [ ] **Step 5: Verify corpus and container**

Run: `uv run pytest workers/ingestion/tests/test_fixture_corpus.py -q`

Run: `docker compose config`

Run: `docker compose up -d fixture-origin && docker compose exec -T fixture-origin wget -qO- http://localhost:8080/health`

Expected: tests pass, Compose validates, and health returns `ok`.

- [ ] **Step 6: Commit**

```bash
git add backend/infra/fixtures backend/docker-compose.yml backend/workers/ingestion/tests/test_fixture_corpus.py
git commit -m "test: add synthetic ingestion source"
```

### Task 4: Implement Crawl4AI Client and Fixture Adapter

**Files:**
- Create: `backend/workers/ingestion/src/carveo_worker/settings.py`
- Create: `backend/workers/ingestion/src/carveo_worker/crawl4ai_client.py`
- Create: `backend/workers/ingestion/src/carveo_worker/adapters/__init__.py`
- Create: `backend/workers/ingestion/src/carveo_worker/adapters/base.py`
- Create: `backend/workers/ingestion/src/carveo_worker/adapters/fixture.py`
- Create: `backend/workers/ingestion/tests/test_crawl4ai_client.py`
- Create: `backend/workers/ingestion/tests/test_fixture_adapter.py`
- Modify: `backend/workers/ingestion/pyproject.toml`

**Interfaces:**
- Produces: `Crawl4AIClient.crawl(urls: Sequence[str]) -> list[CrawlDocument]`.
- Produces: `SourceAdapter.discover(query) -> DiscoveryResult` and `SourceAdapter.extract(reference) -> RawListing`.
- Consumes: source policy authorization before every client call.

`CrawlDocument` contains `url`, `html`, `status_code`, `success`, and sanitized `error`. `DiscoveryResult` contains deduplicated `references`, `visited_pages`, `discovery_complete`, and optional bounded `error_code`. The `SourceAdapter` protocol receives its `SourceProfile`, `SourcePolicy`, and `Crawl4AIClient` at construction.

- [ ] **Step 1: Test request authentication and response validation**

Use `httpx.MockTransport` to assert `POST /crawl`, `Authorization: Bearer <token>`, `stream: false`, bounded URLs per request, a finite timeout, and strict result count/URL matching.

- [ ] **Step 2: Test failure classification**

Cover connect timeout -> `unavailable`, read timeout -> `timeout`, 401/403 -> `authentication`, 429 -> `rate_limited`, opaque 500 -> `server_error`, unsuccessful result containing anti-bot evidence -> `blocked`, malformed JSON -> `invalid_response`, and missing result -> `invalid_response`.

- [ ] **Step 3: Test deterministic adapter extraction**

Assert JSON-LD wins when both paths exist, CSS fallback handles its dedicated page, duplicate discovery collapses by source identity, Arabic text is unchanged, malformed content yields `RejectedListing`, and incomplete search parsing returns `discovery_complete=False`.

- [ ] **Step 4: Run tests and confirm failure**

Run: `uv run pytest workers/ingestion/tests/test_crawl4ai_client.py workers/ingestion/tests/test_fixture_adapter.py -q`

Expected: new imports fail.

- [ ] **Step 5: Implement settings, typed client, and adapter**

```python
class Crawl4AIClient:
    async def crawl(self, urls: Sequence[str]) -> list[CrawlDocument]:
        response = await self._http.post(
            "/crawl",
            headers={"Authorization": f"Bearer {self._token}"},
            json={
                "urls": list(urls),
                "browser_config": {"type": "BrowserConfig", "headless": True},
                "crawler_config": {"type": "CrawlerRunConfig", "stream": False},
            },
        )
        return self._decode(response, expected_urls=urls)
```

The adapter must receive permitted URLs from its own builder; callers cannot pass a URL through `SourceQuery`.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest workers/ingestion/tests/test_crawl4ai_client.py workers/ingestion/tests/test_fixture_adapter.py -q`

Run: `uv lock --check`

```bash
git add backend/workers/ingestion backend/uv.lock
git commit -m "feat: add fixture Crawl4AI adapter"
```

### Task 5: Normalize Listings Without Inventing Evidence

**Files:**
- Create: `backend/workers/ingestion/src/carveo_worker/normalization.py`
- Create: `backend/workers/ingestion/tests/test_normalization.py`

**Interfaces:**
- Consumes: `RawListing`.
- Produces: `normalize_listing(raw: RawListing, now: datetime) -> NormalizedListing | RejectedListing`.

- [ ] **Step 1: Write table-driven normalization tests**

Cover AED values with separators, km values, model year, UAE city aliases, GCC/imported specification values, seller type, image ordering, missing condition evidence, Arabic source text, unsupported mileage units, missing required price, and invalid source URL.

```python
def test_absent_condition_claims_become_unknown_not_positive() -> None:
    result = normalize_listing(raw_listing(condition_claims=[]), NOW)
    assert isinstance(result, NormalizedListing)
    assert [item.kind for item in result.condition_evidence] == ["unknown"]
```

- [ ] **Step 2: Run and confirm failure**

Run: `uv run pytest workers/ingestion/tests/test_normalization.py -q`

Expected: `normalize_listing` is unavailable.

- [ ] **Step 3: Implement small, named normalizers**

Implement `normalize_price`, `normalize_mileage`, `normalize_city`, `normalize_specifications`, `normalize_seller_type`, and `normalize_condition_evidence`. Every transformed field retains its original source text in the normalized contract's audit map. Unsupported or missing required values return a bounded rejection code.

- [ ] **Step 4: Verify and commit**

Run: `uv run pytest workers/ingestion/tests/test_normalization.py -q`

```bash
git add backend/workers/ingestion/src/carveo_worker/normalization.py backend/workers/ingestion/tests/test_normalization.py
git commit -m "feat: normalize fixture listings"
```

### Task 6: Implement Transactional Ingestion Persistence and Lifecycle

**Files:**
- Create: `backend/packages/carveo-core/src/carveo_core/ingestion.py`
- Create: `backend/packages/carveo-core/src/carveo_core/ingestion_sql_repository.py`
- Create: `backend/packages/carveo-core/tests/test_ingestion_repository.py`
- Modify: `backend/packages/carveo-core/src/carveo_core/sql_repository.py`
- Modify: `backend/packages/carveo-core/tests/test_catalogue.py`

**Interfaces:**
- Produces: `IngestionRepository.create_run`, `claim_run`, `record_item`, `upsert_listing`, `finalize_run`, `reconcile_absent`, `mark_failed`, `purge_due`.
- Produces: `ListingWriteOutcome` values `created`, `updated`, `unchanged`, `restored`.
- Preserves: `SqlAlchemyCatalogueRepository` only returns active listings and public Carveo media URLs.

`CreateRun` contains source ID, `SourceQuery`, trigger, hourly correlation key, adapter version, parser version, and queued timestamp. `ListingWriteOutcome` contains outcome, listing UUID, public ID, price-observation-created flag, and obsolete media storage keys. `PurgeSummary` contains deleted listing/artifact/run counts and object storage keys that must be removed after the database commit.

- [ ] **Step 1: Write PostgreSQL repository tests**

Use the existing Testcontainers pattern and test:

- source/query/hour correlation uniqueness;
- one malformed item cannot roll back another listing;
- identical writes are unchanged and do not add price observations;
- changed price adds exactly one observation;
- changed non-price fields do not add a price observation;
- complete miss 1 -> missing, miss 2 -> missing, miss 3 -> removed;
- incomplete discovery does not change miss counters;
- rediscovery before purge restores the same public ID;
- source-sold removes catalogue visibility immediately;
- concurrent finalization reconciles only once.

- [ ] **Step 2: Run and confirm failure**

Run: `uv run pytest packages/carveo-core/tests/test_ingestion_repository.py -q -m integration`

Expected: import failure for `SqlAlchemyIngestionRepository`.

- [ ] **Step 3: Define the repository protocol and outcomes**

```python
class IngestionRepository(Protocol):
    async def create_run(self, command: CreateRun) -> CrawlRunSummary: ...
    async def upsert_listing(self, run_id: UUID, listing: NormalizedListing) -> ListingWriteOutcome: ...
    async def finalize_run(self, run_id: UUID, *, discovery_complete: bool) -> CrawlRunSummary: ...
    async def purge_due(self, now: datetime) -> PurgeSummary: ...
```

- [ ] **Step 4: Implement per-listing transactions and locked finalization**

Use `SELECT ... FOR UPDATE` around the Source Listing upsert and run finalization. Use database uniqueness as the final idempotency defense. Reconciliation only executes when `discovery_complete` is true and run status is not terminal.

- [ ] **Step 5: Implement exact purge semantics**

Before deleting a listing, set its price observations' `listing_id` to null. Delete buyer shortlist/comparison references, listing-specific run-item links, extraction artifacts, evidence, photos, duplicate offers, and the listing in one transaction. Return storage keys for object deletion after commit; failed object deletion remains retryable without restoring the database record.

- [ ] **Step 6: Update catalogue mapping**

Emit `/api/v1/media/{photo_id}` for cached photos. Filter `price_history` to observations still linked to the current listing. Continue hiding missing, removed, and source-sold records from buyer APIs.

- [ ] **Step 7: Verify and commit**

Run: `uv run pytest packages/carveo-core/tests/test_ingestion_repository.py packages/carveo-core/tests/test_catalogue.py -q -m integration`

```bash
git add backend/packages/carveo-core
git commit -m "feat: persist ingestion lifecycle"
```

### Task 7: Add MinIO Media Cache and Stable API Delivery

**Files:**
- Create: `backend/workers/ingestion/src/carveo_worker/storage.py`
- Create: `backend/workers/ingestion/src/carveo_worker/media.py`
- Create: `backend/workers/ingestion/tests/test_media.py`
- Create: `backend/apps/api/src/carveo_api/media.py`
- Create: `backend/apps/api/tests/test_media.py`
- Modify: `backend/apps/api/src/carveo_api/main.py`
- Modify: `backend/apps/api/src/carveo_api/settings.py`
- Modify: `backend/workers/ingestion/pyproject.toml`
- Modify: `backend/apps/api/pyproject.toml`
- Create: `backend/infra/minio/init.sh`
- Modify: `backend/docker-compose.yml`

**Interfaces:**
- Produces: `ObjectStorage.put_if_absent`, `open`, `delete_many`.
- Produces: `MediaCache.refresh(listing_id, photos) -> MediaCacheResult`.
- Produces: `GET /api/v1/media/{photo_id}` with streaming bytes, immutable ETag, and private storage internals.

- [ ] **Step 1: Test media security and atomicity**

Test HTTPS/HTTP scheme allowlist, exact fixture host allowlist, redirect revalidation, content-type allowlist, 10 MiB streamed byte ceiling, maximum image count, hash reuse, duplicate bytes, partial download failure preserving the previous image set, and query-string removal from logs.

- [ ] **Step 2: Test the API route**

Use an injected storage stub. Assert 200 bytes/content type/ETag, 304 for matching `If-None-Match`, 404 for unknown photo, and absence of `storage_key`, bucket, MinIO host, and credentials from all responses.

- [ ] **Step 3: Run and confirm failure**

Run: `uv run pytest workers/ingestion/tests/test_media.py apps/api/tests/test_media.py -q`

Expected: media modules and route are absent.

- [ ] **Step 4: Implement S3 storage and media refresh**

Use an async S3-compatible client behind the protocol. Key objects by `sha256/<first-two>/<full-hash>.<ext>`. Upload all new objects before the repository swaps photo rows. Delete superseded objects only when no photo row references their content hash.

- [ ] **Step 5: Add MinIO and bucket initialization**

Add private `minio` and one-shot `minio-init` services, a `minio-data` volume, health checks, non-default environment-backed credentials, and no browser-facing port. Make API and worker depend on successful bucket initialization.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest workers/ingestion/tests/test_media.py apps/api/tests/test_media.py -q`

Run: `uv lock --check`

Run: `docker compose config`

```bash
git add backend/apps/api backend/workers/ingestion backend/infra/minio backend/docker-compose.yml backend/uv.lock
git commit -m "feat: cache listing media in MinIO"
```

### Task 8: Orchestrate Resumable Runs Through Dramatiq and Redis

**Files:**
- Create: `backend/workers/ingestion/src/carveo_worker/coordinator.py`
- Modify: `backend/workers/ingestion/src/carveo_worker/tasks.py`
- Modify: `backend/workers/ingestion/src/carveo_worker/broker.py`
- Create: `backend/workers/ingestion/tests/test_coordinator.py`
- Modify: `backend/workers/ingestion/tests/test_worker.py`

**Interfaces:**
- Produces actors: `start_ingestion_run(run_id)`, `process_run_item(run_item_id)`, `finalize_ingestion_run(run_id)`, `purge_expired_data(cutoff_iso)`.
- Produces: Redis idempotency key `carveo:ingestion:{source}:{query}:{scenario}:{hour}` with bounded TTL.
- Consumes: adapter, normalizer, repository, media cache from Tasks 4-7.

- [ ] **Step 1: Write coordinator state-machine tests**

Test policy rejection before client invocation, successful discovery fan-out, one rejected item with partial completion, search failure without reconciliation, detail failure preserving an existing listing, resumed unprocessed items, terminal-run no-op, and stale-running detection.

- [ ] **Step 2: Extend worker tests**

Assert actor queue names, JSON-safe arguments, transient retry settings, permanent failures using `dramatiq.middleware.CurrentMessage` failure without retry, and exhausted retry dead-letter persistence.

- [ ] **Step 3: Run and confirm failure**

Run: `uv run pytest workers/ingestion/tests/test_coordinator.py workers/ingestion/tests/test_worker.py -q`

Expected: orchestration actors are absent.

- [ ] **Step 4: Implement a dependency-built coordinator**

```python
class IngestionCoordinator:
    async def discover(self, run_id: UUID) -> list[UUID]: ...
    async def process_item(self, run_item_id: UUID) -> CrawlRunItemResult: ...
    async def finalize(self, run_id: UUID) -> CrawlRunSummary: ...
```

Construct production dependencies in one `build_coordinator(settings)` function. Tests inject protocols directly. Actors remain thin and convert string UUIDs at their boundary.

- [ ] **Step 5: Verify stub and Redis integration behavior**

Run: `uv run pytest workers/ingestion/tests/test_coordinator.py workers/ingestion/tests/test_worker.py -q`

Run: `uv run pytest workers/ingestion/tests/test_worker.py -q -m integration`

Expected: enqueue, acknowledgement, retry exhaustion, and dead-letter assertions pass.

- [ ] **Step 6: Commit**

```bash
git add backend/workers/ingestion
git commit -m "feat: orchestrate ingestion runs"
```

### Task 9: Add Hourly Scheduling, Maintenance, and On-Demand CLI

**Files:**
- Modify: `backend/workers/ingestion/src/carveo_worker/beat.py`
- Create: `backend/workers/ingestion/src/carveo_worker/cli.py`
- Create: `backend/workers/ingestion/tests/test_schedule.py`
- Create: `backend/workers/ingestion/tests/test_cli.py`
- Modify: `backend/workers/ingestion/pyproject.toml`
- Modify: `backend/docker-compose.yml`
- Modify: `backend/README.md`

**Interfaces:**
- Produces: hourly job ID `fixture-ingestion-hourly`, daily purge job ID `ingestion-retention-daily`.
- Produces command: `uv run carveo-ingest fixture --scenario baseline --query popular-uae --wait`.

- [ ] **Step 1: Test scheduler registration and test disablement**

Assert one coalescing hourly ingestion job, one daily retention job, `max_instances=1`, deterministic job IDs, and zero ingestion jobs when `CARVEO_INGESTION_SCHEDULER_ENABLED=false`.

- [ ] **Step 2: Test CLI validation and enqueueing**

Assert only manifest scenarios and internal query keys are accepted, output includes a run UUID, `--wait` exits zero on completion and nonzero on failure/timeout, and no URL option exists.

- [ ] **Step 3: Run and confirm failure**

Run: `uv run pytest workers/ingestion/tests/test_schedule.py workers/ingestion/tests/test_cli.py -q`

Expected: schedule registration and CLI entry point are absent.

- [ ] **Step 4: Implement scheduler and CLI**

Keep the existing 30-second health monitor. Add separate APScheduler jobs and entry point:

```toml
[project.scripts]
carveo-ingest = "carveo_worker.cli:main"
```

Set `CARVEO_INGESTION_SCHEDULER_ENABLED=true` only for local Compose Beat; test environment builders set it false.

- [ ] **Step 5: Verify and commit**

Run: `uv run pytest workers/ingestion/tests/test_schedule.py workers/ingestion/tests/test_cli.py -q`

Run: `docker compose config`

```bash
git add backend/workers/ingestion backend/docker-compose.yml backend/README.md backend/uv.lock
git commit -m "feat: schedule fixture ingestion"
```

### Task 10: Instrument Ingestion and Provision Operations Views

**Files:**
- Create: `backend/workers/ingestion/src/carveo_worker/metrics.py`
- Create: `backend/workers/ingestion/tests/test_metrics.py`
- Modify: `backend/workers/ingestion/src/carveo_worker/coordinator.py`
- Modify: `backend/infra/observability/prometheus/alerts.yml`
- Modify: `backend/infra/observability/grafana/dashboards/carveo-operations.json`
- Modify: `backend/workers/ingestion/src/carveo_worker/logging.py`

**Interfaces:**
- Produces metrics: `carveo_ingestion_runs_total`, `carveo_ingestion_run_duration_seconds`, `carveo_ingestion_items_total`, `carveo_ingestion_media_total`, `carveo_ingestion_retries_total`, `carveo_ingestion_dead_letters_total`, `carveo_ingestion_active_run_age_seconds`, `carveo_ingestion_stale_runs`, and `carveo_crawl4ai_request_duration_seconds`.
- Labels are limited to source key, trigger, stage, and bounded outcome/error enums.

- [ ] **Step 1: Write metrics and log-redaction tests**

Assert counters change once per state transition, retry/dead-letter counters are not double-counted, no label includes run/listing IDs or URLs, and captured JSON logs exclude raw HTML, tokens, cookies, authorization headers, full image query strings, and MinIO credentials.

- [ ] **Step 2: Run and confirm failure**

Run: `uv run pytest workers/ingestion/tests/test_metrics.py -q`

Expected: ingestion collectors are absent.

- [ ] **Step 3: Implement bounded collectors and structured event helpers**

Use an injectable `CollectorRegistry` in tests. Emit correlation details as structured log fields, not metric labels. Log only sanitized error categories.

- [ ] **Step 4: Add alerts and dashboard panels**

Add alerts for no successful hourly run in two hours, rejection ratio above 20% for 15 minutes, Crawl4AI failures, stale active runs, dead letters, and purge failures. Add Grafana rows for throughput/success, stage outcomes, catalogue lifecycle, media, queue/retries, and stale runs.

- [ ] **Step 5: Verify provisioning and commit**

Run: `uv run pytest workers/ingestion/tests/test_metrics.py -q`

Run: `docker compose config`

Run: `docker compose run --rm prometheus promtool check config /etc/prometheus/prometheus.yml`

```bash
git add backend/workers/ingestion backend/infra/observability
git commit -m "feat: monitor ingestion pipeline"
```

### Task 11: Verify Public Contracts and the Integrated Buyer Journey

**Files:**
- Modify: `backend/apps/api/tests/test_api.py`
- Modify: `backend/apps/api/tests/test_contract.py`
- Modify: `backend/contracts/openapi.json`
- Modify: `frontend/src/contracts/api.ts`
- Modify: `frontend/src/repositories/api-catalogue-repository.test.ts`
- Create: `frontend/e2e/ingested-catalogue.spec.ts`
- Create: `backend/workers/ingestion/tests/test_container_journey.py`

**Interfaces:**
- Confirms: ingestion writes remain compatible with `CatalogueRepository` and every photo resolves through a Carveo URL.
- Confirms: the browser never receives internal fixture-origin or MinIO addresses.

- [ ] **Step 1: Add contract and repository regressions**

Assert `Listing.photos` contains `/api/v1/media/{uuid}` URLs after ingestion, source attribution remains fixture-labelled, Arabic titles survive JSON serialization and Zod parsing, and missing condition evidence reads as unknown.

- [ ] **Step 2: Add a container journey test**

The test starts from a fresh migrated database, enqueues `baseline`, waits for a successful run, queries the API, downloads one image, runs `unchanged`, applies `changed`, verifies one price observation and image replacement, then runs absence/restoration scenarios. It must never use a live hostname.

- [ ] **Step 3: Add the Playwright buyer journey**

Search for an ingested fixture vehicle, open its detail page, verify the proxied image loads, verify Arabic text on an Arabic fixture, shortlist it, compare it, and confirm no request URL targets `fixture-origin`, `minio`, or port `9000`.

- [ ] **Step 4: Run tests and observe initial failures**

Run: `uv run pytest workers/ingestion/tests/test_container_journey.py apps/api/tests/test_api.py apps/api/tests/test_contract.py -q -m integration`

Run: `bun run test -- src/repositories/api-catalogue-repository.test.ts`

Expected: failures identify ungenerated contracts or missing integrated fixture data.

- [ ] **Step 5: Export OpenAPI and regenerate TypeScript contracts**

Run: `uv run python -m carveo_api.export_openapi`

Run: `bun run contracts:generate`

Do not hand-edit generated contract files.

- [ ] **Step 6: Run integrated verification**

Run: `uv run pytest workers/ingestion/tests/test_container_journey.py apps/api/tests/test_api.py apps/api/tests/test_contract.py -q -m integration`

Run: `bun run test -- src/repositories/api-catalogue-repository.test.ts`

Run: `bun run test:e2e:api -- e2e/ingested-catalogue.spec.ts`

Expected: all selected contract and buyer-journey checks pass.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/api backend/contracts frontend/src/contracts frontend/src/repositories frontend/e2e backend/workers/ingestion/tests/test_container_journey.py
git commit -m "test: verify ingested catalogue journey"
```

### Task 12: Complete Retention, Runbook, and Milestone Verification

**Files:**
- Create: `backend/docs/ingestion-runbook.md`
- Modify: `backend/README.md`
- Modify: `codex.md`
- Modify: `backend/workers/ingestion/CONTEXT.md`
- Modify: `CONTEXT-MAP.md`

**Interfaces:**
- Documents: start/stop, health, on-demand run, scenario selection, metrics, dashboard, retry/dead-letter diagnosis, kill switch, retention, and clean recovery.
- Confirms: all Option A acceptance criteria from the approved spec.

- [ ] **Step 1: Write the operational runbook**

Include exact commands for a fresh start, baseline run, terminal run lookup, API verification, media verification, Prometheus target checks, Grafana dashboard access, source kill switch, stale-run handling, dead-letter inspection, seven-day listing/media purge, seven-day artifact purge, and 90-day run-detail purge. State prominently that fixtures are synthetic and live crawling is prohibited.

- [ ] **Step 2: Run the complete backend quality gate**

Run: `uv run pytest`

Run: `uv run ruff check .`

Run: `uv run mypy`

Run: `uv lock --check`

Expected: every command exits zero.

- [ ] **Step 3: Run the complete frontend quality gate**

Run: `bun run typecheck`

Run: `bun run test`

Run: `bun run contracts:check`

Run: `bun run build`

Expected: every command exits zero.

- [ ] **Step 4: Run the full container acceptance journey**

Run: `docker compose down -v`

Run: `docker compose up --build -d`

Run: `docker compose ps`

Run: `uv run carveo-ingest fixture --scenario baseline --query popular-uae --wait`

Verify `/health`, `/ready`, catalogue results, one media URL, worker and Beat health, Prometheus targets, and the Grafana ingestion panels. Run `changed`, `missing-1`, `missing-2`, `removed`, and `restored` scenarios and compare database/run counters with the spec.

- [ ] **Step 5: Run the end-to-end browser suite**

Run: `bun run test:e2e:api`

Expected: the API-backed marketplace and fixture-ingestion journey pass with no page-level horizontal overflow or leaked internal storage URLs.

- [ ] **Step 6: Refresh the project knowledge graph**

Run: `graphify update .`

Expected: `graphify-out/graph.json`, report, and related generated files represent the new ingestion modules and relationships.

- [ ] **Step 7: Commit the verified milestone documentation**

```bash
git add backend/docs backend/README.md codex.md backend/workers/ingestion/CONTEXT.md CONTEXT-MAP.md graphify-out
git commit -m "docs: complete fixture ingestion runbook"
```

---

## Acceptance Checklist

- [ ] Fresh Compose startup reports healthy PostgreSQL, Redis, API, worker, Beat, Crawl4AI, fixture origin, MinIO, Prometheus, Grafana, and web services.
- [ ] On-demand and hourly fixture runs use the same Dramatiq pipeline and collapse duplicate source/query/scenario/hour requests.
- [ ] English and Arabic synthetic listings reach PostgreSQL, FastAPI, and Next.js without source-text loss.
- [ ] Identical runs are idempotent; price or image changes produce exactly the expected history and media swap.
- [ ] Failed/partial discovery never advances absence state; three complete successful misses remove a listing.
- [ ] A listing restored before purge keeps its public identity and linked history.
- [ ] Listing records, buyer references, source-specific artifacts, and cached images are deleted seven days after removal.
- [ ] Retained price observations are anonymized; run details expire after 90 days.
- [ ] No buyer-controlled arbitrary URL can reach Crawl4AI or the media downloader.
- [ ] Grafana displays actual ingestion metrics collected by Prometheus and alerts validate with `promtool`.
- [ ] Backend, frontend, contract, migration, container, accessibility, and browser checks pass.
- [ ] No AWS, Vercel, live-source, or AI implementation is included.

## Reference Notes

- Crawl4AI 0.9.x Docker authentication requires `CRAWL4AI_API_TOKEN` and bearer authorization for protected endpoints: <https://github.com/unclecode/crawl4ai/blob/main/CHANGELOG.md>
- Crawl4AI 0.9.2 `/crawl` may return an opaque HTTP 500 for unsuccessful waits; the client therefore classifies HTTP and per-result failures and never treats them as empty success: <https://github.com/unclecode/crawl4ai/issues/2133>
- PostgreSQL remains the behavioral test database; SQLite is not an ingestion substitute.
