import type { CatalogueRepository } from "@/repositories/catalogue-repository";
import type { Listing, ListingPage, ListingQuery, ModelMarketSummary } from "@/domain/schemas";
import { calculateDealPosition, median } from "@/domain/valuation";

function matches(listing: Listing, query: ListingQuery) {
  const text = `${listing.title} ${listing.make} ${listing.model} ${listing.trim} ${listing.city}`.toLowerCase();
  const hasEvidence = listing.conditionEvidence.some((evidence) => evidence.kind !== "unknown");
  return (
    (!query.q || text.includes(query.q.toLowerCase())) &&
    (!query.make.length || query.make.includes(listing.make)) &&
    (!query.model.length || query.model.includes(listing.model)) &&
    (!query.bodyType.length || query.bodyType.includes(listing.bodyType)) &&
    (!query.city.length || query.city.includes(listing.city)) &&
    (!query.specifications.length || query.specifications.includes(listing.specifications)) &&
    (!query.sellerType.length || query.sellerType.includes(listing.sellerType)) &&
    (!query.evidence.length || (query.evidence.includes("stated") && hasEvidence)) &&
    (query.yearMin === undefined || listing.year >= query.yearMin) &&
    (query.yearMax === undefined || listing.year <= query.yearMax) &&
    (query.priceMin === undefined || listing.price >= query.priceMin) &&
    (query.priceMax === undefined || listing.price <= query.priceMax) &&
    (query.mileageMax === undefined || listing.mileageKm <= query.mileageMax)
  );
}

export class FixtureCatalogueRepository implements CatalogueRepository {
  constructor(private readonly listings: Listing[]) {}

  private enrich(listing: Listing): Listing {
    const comparables = this.listings.filter((candidate) =>
      candidate.id !== listing.id && candidate.make === listing.make && candidate.model === listing.model && Math.abs(candidate.year - listing.year) <= 2,
    );
    return { ...listing, dealPosition: calculateDealPosition(listing.price, comparables.map((item) => item.price)) };
  }

  async search(query: ListingQuery): Promise<ListingPage> {
    const items = this.listings.filter((listing) => matches(listing, query)).map((listing) => this.enrich(listing));
    const sorters: Record<ListingQuery["sort"], (a: Listing, b: Listing) => number> = {
      "best-match": (a, b) => (a.dealPosition?.differencePercent ?? 0) - (b.dealPosition?.differencePercent ?? 0),
      "best-deal": (a, b) => (a.dealPosition?.differencePercent ?? 0) - (b.dealPosition?.differencePercent ?? 0),
      newest: (a, b) => Date.parse(b.firstSeenAt) - Date.parse(a.firstSeenAt),
      "lowest-price": (a, b) => a.price - b.price,
      "lowest-mileage": (a, b) => a.mileageKm - b.mileageKm,
    };
    items.sort(sorters[query.sort]);
    const start = (query.page - 1) * query.pageSize;
    return { items: items.slice(start, start + query.pageSize), total: items.length, page: query.page, pageSize: query.pageSize, pageCount: Math.max(1, Math.ceil(items.length / query.pageSize)) };
  }

  async getById(id: string) { const found = this.listings.find((listing) => listing.id === id); return found ? this.enrich(found) : null; }

  async getRelated(id: string, limit = 4) {
    const current = this.listings.find((listing) => listing.id === id);
    if (!current) return [];
    return this.listings
      .filter((listing) => listing.id !== id)
      .sort((a, b) => Number(b.make === current.make) - Number(a.make === current.make) || Number(b.bodyType === current.bodyType) - Number(a.bodyType === current.bodyType))
      .slice(0, limit)
      .map((listing) => this.enrich(listing));
  }

  async compare(ids: string[]) {
    return ids.slice(0, 4).map((id) => this.listings.find((listing) => listing.id === id)).filter((listing): listing is Listing => Boolean(listing)).map((listing) => this.enrich(listing));
  }

  async getAll() { return this.listings.map((listing) => this.enrich(listing)); }

  async getModelSummary(make: string, model: string): Promise<ModelMarketSummary | null> {
    const matches = this.listings.filter((listing) => listing.make.toLowerCase() === make.toLowerCase() && listing.model.toLowerCase() === model.toLowerCase());
    if (!matches.length) return null;
    const prices = matches.map((listing) => listing.price);
    const mileages = matches.map((listing) => listing.mileageKm);
    return { make: matches[0].make, model: matches[0].model, activeListings: matches.length, medianPrice: median(prices)!, minPrice: Math.min(...prices), maxPrice: Math.max(...prices), minMileage: Math.min(...mileages), maxMileage: Math.max(...mileages), lastUpdatedAt: matches.map((item) => item.lastSeenAt).sort().at(-1)! };
  }

}
