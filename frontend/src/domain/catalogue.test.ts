import { describe, expect, it } from "vitest";
import { fixtureCatalogue } from "@/data/fixture-catalogue";
import { FixtureCatalogueRepository } from "@/repositories/fixture-catalogue-repository";
import { parseListingQuery, slugifyVehicleName, toListingSearchParams } from "@/domain/query";

describe("listing query", () => {
  it("normalizes URL values into a safe UAE query", () => {
    const query = parseListingQuery(
      new URLSearchParams("make=Mercedes-Benz&bodyType=SUV&priceMax=250000&page=0&pageSize=500&sort=lowest-price"),
    );

    expect(query).toEqual(
      expect.objectContaining({
        market: "ae",
        make: ["Mercedes-Benz"],
        bodyType: ["SUV"],
        priceMax: 250000,
        page: 1,
        pageSize: 24,
        sort: "lowest-price",
      }),
    );
  });

  it("round-trips multi-value filters without emitting defaults", () => {
    const params = toListingSearchParams({
      ...parseListingQuery(new URLSearchParams()),
      make: ["Toyota", "Nissan"],
      city: ["Dubai", "Abu Dhabi"],
      specifications: ["GCC"],
    });

    expect(params.getAll("make")).toEqual(["Toyota", "Nissan"]);
    expect(params.getAll("city")).toEqual(["Dubai", "Abu Dhabi"]);
    expect(params.has("page")).toBe(false);
  });

  it("creates stable market-route slugs for vehicle names", () => {
    expect(slugifyVehicleName("Mercedes-Benz C 200")).toBe("mercedes-benz-c-200");
    expect(slugifyVehicleName("  Land Cruiser  ")).toBe("land-cruiser");
  });
});

describe("fixture catalogue repository", () => {
  const repository = new FixtureCatalogueRepository(fixtureCatalogue);

  it("provides the planned breadth of UAE fixture inventory", () => {
    expect(fixtureCatalogue).toHaveLength(24);
    expect(new Set(fixtureCatalogue.map((listing) => listing.make)).size).toBeGreaterThanOrEqual(8);
    expect(new Set(fixtureCatalogue.map((listing) => listing.bodyType)).size).toBeGreaterThanOrEqual(5);
  });

  it("applies intersecting filters and paginates the result", async () => {
    const page = await repository.search({
      ...parseListingQuery(new URLSearchParams()),
      make: ["Toyota"],
      bodyType: ["SUV"],
      priceMax: 180000,
      pageSize: 2,
    });

    expect(page.items).toHaveLength(2);
    expect(page.total).toBeGreaterThanOrEqual(2);
    expect(page.items.every((listing) => listing.make === "Toyota" && listing.bodyType === "SUV")).toBe(true);
  });

  it("sorts price ascending with unknown values last", async () => {
    const page = await repository.search({
      ...parseListingQuery(new URLSearchParams()),
      sort: "lowest-price",
      pageSize: 24,
    });
    const prices = page.items.map((listing) => listing.price);

    expect(prices).toEqual([...prices].sort((a, b) => a - b));
  });

  it("returns listing detail and related models through the repository boundary", async () => {
    const listing = await repository.getById("cv-toyota-land-cruiser-2022-01");
    const related = await repository.getRelated("cv-toyota-land-cruiser-2022-01", 3);

    expect(listing?.title).toContain("Land Cruiser");
    expect(related).toHaveLength(3);
    expect(related.every((item) => item.id !== listing?.id)).toBe(true);
  });

  it("preserves requested order while capping comparison at four", async () => {
    const ids = [fixtureCatalogue[4].id, fixtureCatalogue[0].id, fixtureCatalogue[8].id, fixtureCatalogue[10].id, fixtureCatalogue[12].id];
    const compared = await repository.compare(ids);

    expect(compared.map((listing) => listing.id)).toEqual(ids.slice(0, 4));
  });

  it("summarizes a model segment and returns null for an unknown model", async () => {
    const summary = await repository.getModelSummary("Toyota", "Land Cruiser");

    expect(summary).toEqual(expect.objectContaining({ activeListings: 4, minPrice: 238000, maxPrice: 289000 }));
    expect(await repository.getModelSummary("Toyota", "Unknown")).toBeNull();
  });

  it("uses model-specific approved media before the body-type fallback", () => {
    expect(fixtureCatalogue.find((listing) => listing.model === "Land Cruiser")?.photos[0]).toBe("/media/toyota-land-cruiser.jpg");
    expect(fixtureCatalogue.find((listing) => listing.model === "C 200")?.photos[0]).toBe("/media/mercedes-c-class.jpg");
  });
});
