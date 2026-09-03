# Ingestion

The ingestion context turns permitted marketplace material into Carveo's source listings while preserving where each claim came from.

## Language

**Source**:
A marketplace or licensed feed from which Carveo may receive vehicle offers under a recorded access policy.
_Avoid_: Website, provider

**Fixture Source**:
A controlled, non-live representation of a Source used to exercise ingestion without contacting that Source.
_Avoid_: Fake marketplace, mock Source

**Source Listing**:
One offer published by a Source, identified within Carveo by the Source and the Source's listing identifier.
_Avoid_: Car, vehicle record

**Ingestion Run**:
One bounded attempt to discover and reconcile Source Listings for a Source.
_Avoid_: Crawl, scrape job

**Active Source Listing**:
A Source Listing observed during the latest successful Ingestion Run for its Source.
_Avoid_: Live car, available vehicle

**Missing Source Listing**:
A previously Active Source Listing not observed during the latest successful Ingestion Run, but not yet considered removed.
_Avoid_: Deleted listing, sold listing

**Removed Source Listing**:
A Source Listing that Carveo considers unavailable after repeated successful Ingestion Runs do not observe it.
_Avoid_: Sold listing, deleted car

**Restored Source Listing**:
A Missing or Removed Source Listing observed again before its retained record is deleted.
_Avoid_: New listing, duplicate listing

**Source-Sold Listing**:
A Source Listing whose Source explicitly states that the offer is sold.
_Avoid_: Removed listing, missing listing
