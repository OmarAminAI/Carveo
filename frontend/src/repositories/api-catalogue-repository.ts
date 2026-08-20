import createClient from "openapi-fetch";
import { z } from "zod";
import type { paths } from "@/contracts/api";
import {
  listingSchema,
  type Listing,
  type ListingPage,
  type ListingQuery,
  type ModelMarketSummary,
} from "@/domain/schemas";
import { toListingSearchParams } from "@/domain/query";
import type { CatalogueRepository } from "@/repositories/catalogue-repository";

const listingPageSchema = z.object({
  items: z.array(listingSchema),
  total: z.number(),
  page: z.number(),
  pageSize: z.number(),
  pageCount: z.number(),
});

const modelSummarySchema = z.object({
  make: z.string(),
  model: z.string(),
  activeListings: z.number(),
  medianPrice: z.number(),
  minPrice: z.number(),
  maxPrice: z.number(),
  minMileage: z.number(),
  maxMileage: z.number(),
  lastUpdatedAt: z.string(),
});

export class ApiCatalogueRepository implements CatalogueRepository {
  private readonly client;
  private readonly baseUrl: string;
  private readonly fetcher: typeof fetch;

  constructor(baseUrl: string, fetcher: typeof fetch = fetch) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.fetcher = fetcher;
    this.client = createClient<paths>({ baseUrl: this.baseUrl, fetch: fetcher });
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await this.fetcher(path, init);
    if (!response.ok) {
      throw new Error(`Catalogue API request failed (${response.status})`);
    }
    return response.json() as Promise<T>;
  }

  async search(query: ListingQuery): Promise<ListingPage> {
    const params = toListingSearchParams(query);
    params.set("market", query.market);
    params.set("pageSize", String(query.pageSize));
    const response = await this.request<unknown>(`${this.baseUrl}/api/v1/listings?${params}`);
    return listingPageSchema.parse(response);
  }

  async getById(id: string): Promise<Listing | null> {
    const { data, response } = await this.client.GET("/api/v1/listings/{listing_id}", {
      params: { path: { listing_id: id } },
    });
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`Catalogue API request failed (${response.status})`);
    return listingSchema.parse(data);
  }

  async getRelated(id: string, limit = 4): Promise<Listing[]> {
    const data = await this.request<unknown>(
      `${this.baseUrl}/api/v1/listings/${encodeURIComponent(id)}/related?limit=${limit}`,
    );
    return z.array(listingSchema).parse(data);
  }

  async compare(ids: string[]): Promise<Listing[]> {
    const data = await this.request<{ items: unknown[] }>(`${this.baseUrl}/api/v1/compare`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ listingIds: ids.slice(0, 4) }),
    });
    return z.array(listingSchema).parse(data.items);
  }

  async getAll(): Promise<Listing[]> {
    const query = parseAllQuery();
    const firstPage = await this.search(query);
    const items = [...firstPage.items];

    for (let page = 2; page <= firstPage.pageCount; page += 1) {
      const nextPage = await this.search({ ...query, page });
      items.push(...nextPage.items);
    }

    return items;
  }

  async getModelSummary(make: string, model: string): Promise<ModelMarketSummary | null> {
    const response = await this.fetcher(`${this.baseUrl}/api/v1/models/${encodeURIComponent(make)}/${encodeURIComponent(model)}/insights`);
    if (response.status === 404) return null;
    if (!response.ok) {
      throw new Error(`Catalogue API request failed (${response.status})`);
    }
    const data = (await response.json()) as { summary: unknown };
    return modelSummarySchema.parse(data.summary);
  }
}

function parseAllQuery(): ListingQuery {
  return {
    market: "ae",
    q: "",
    make: [],
    model: [],
    bodyType: [],
    specifications: [],
    sellerType: [],
    evidence: [],
    city: [],
    sort: "newest",
    page: 1,
    pageSize: 48,
  };
}
