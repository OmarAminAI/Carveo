import type { Listing, ListingPage, ListingQuery, ModelMarketSummary } from "@/domain/schemas";

export interface CatalogueRepository {
  search(query: ListingQuery): Promise<ListingPage>;
  getById(id: string): Promise<Listing | null>;
  getRelated(id: string, limit?: number): Promise<Listing[]>;
  compare(ids: string[]): Promise<Listing[]>;
  getAll(): Promise<Listing[]>;
  getModelSummary(make: string, model: string): Promise<ModelMarketSummary | null>;
}
