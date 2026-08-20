import { describe, expect, it, vi } from "vitest";
import { fixtureCatalogue } from "@/data/fixture-catalogue";
import { parseListingQuery } from "@/domain/query";
import { ApiCatalogueRepository } from "@/repositories/api-catalogue-repository";

describe("ApiCatalogueRepository", () => {
  it("serializes repeated filters and validates the response", async () => {
    const fetcher = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(JSON.stringify({ items: [fixtureCatalogue[0]], total: 1, page: 1, pageSize: 12, pageCount: 1 }), { status: 200, headers: { "content-type": "application/json" } }));
    const repository = new ApiCatalogueRepository("http://api.test", fetcher);
    const query = parseListingQuery(new URLSearchParams("make=Toyota&make=Nissan&bodyType=SUV"));

    const result = await repository.search(query);

    expect(result.items[0].id).toBe(fixtureCatalogue[0].id);
    const url = String(fetcher.mock.calls[0][0]);
    expect(url).toContain("make=Toyota");
    expect(url).toContain("make=Nissan");
    expect(url).toContain("bodyType=SUV");
  });

  it("loads every page when the complete catalogue is requested", async () => {
    const fetcher = vi.fn(async (input: RequestInfo | URL) => {
      const page = new URL(String(input)).searchParams.get("page");
      const item = page === "2" ? fixtureCatalogue[1] : fixtureCatalogue[0];
      return new Response(
        JSON.stringify({ items: [item], total: 2, page: Number(page), pageSize: 48, pageCount: 2 }),
        { status: 200, headers: { "content-type": "application/json" } },
      );
    });
    const repository = new ApiCatalogueRepository("http://api.test", fetcher);

    const listings = await repository.getAll();

    expect(listings.map((listing) => listing.id)).toEqual([
      fixtureCatalogue[0].id,
      fixtureCatalogue[1].id,
    ]);
    expect(fetcher).toHaveBeenCalledTimes(2);
  });
});
