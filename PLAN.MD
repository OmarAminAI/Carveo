# Carveo Marketplace Plan

## Product Direction

Carveo is a search-first used-car marketplace for the UAE. It brings comparable listings into a single catalogue, shows a transparent typical market price, highlights potential deal quality, and sends buyers to the original listing to continue a purchase.

The first release is English UAE (`/en-ae`). The routing, currency, and source contracts are market-aware so later GCC launches can add Arabic/RTL and local currency rules without replacing the core product.

## Release Scope

- Homepage with direct search, make/body type/budget exploration, deal highlights, recent inventory, and source transparency.
- Browse results with query-backed filters, price/mileage/newness sorting, comparison selection, anonymous saved searches, and optional chat refinement.
- Listing details with source claims, price context, features, and an outbound source link.
- Side-by-side comparison for up to four listings.
- A normalized UAE fixture catalogue while production source approval is pending.

The release excludes accounts, alerts, finance, guides, newsletters, app promotion, Saudi inventory, and Haraj ingestion.

## Catalogue and Valuation

`GET /api/v1/listings` is the primary catalogue interface. It supports UAE market, text, make, model, body type, year, price, mileage, regional-specification, seller, sort, and pagination parameters. Listing detail, comparison, market metadata, and anonymous saved-search endpoints build on the same listing contract.

Each listing carries source metadata, structured vehicle fields, source-stated condition evidence, features, freshness, and historical-price storage. The UI labels unavailable condition data as unknown. It does not claim that a car is accident-free or inspected unless the source states that.

Typical market price is a robust median over comparable active UAE listings by make, model, nearby year, and regional specifications. Deal labels are a comparison signal, not a valuation guarantee, inspection, or purchase recommendation.

## Ingestion Rules

Crawl4AI runs behind a source registry. Every adapter must implement discovery and extraction against a normalized listing contract. The worker deduplicates hourly popular and anonymous-profile refresh queries, records raw extraction metadata, and never runs an adapter unless its source has explicit `approved` authorization and is enabled.

Dubizzle is the intended first UAE adapter, but remains disabled until written permission, an approved API, or a licensed feed is recorded. Haraj is out of scope: its published terms prohibit the automated/non-human collection and reuse required by this product. Any Saudi launch requires a separate approved source strategy.

## Delivery Sequence

1. Maintain the UAE catalogue, API contracts, price observations, anonymous saved searches, and marketplace UI using approved fixtures.
2. Complete source legal/commercial review; seed an approved source record and add adapter-specific saved-page contract tests.
3. Enable the Dubizzle Crawl4AI adapter with per-source rate limits, scheduled refreshes, source health telemetry, and failure handling.
4. Expand only after each new market has a compliant data source, localized content rules, and valuation coverage.

## Quality Bar

- API tests cover filters, detail, comparison, saved searches, pagination, and market-price labels.
- Worker tests cover authorization gating, hourly queue deduplication, normalization, missing-condition behavior, and adapter failures.
- Frontend tests cover direct search, filters, comparison, saved-search state, loading/error/empty states, and chat refinement.
- Browser checks cover all marketplace routes at desktop and mobile widths with no horizontal overflow.
