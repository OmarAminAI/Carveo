import { describe, expect, it, vi } from "vitest";
import { fixtureCatalogue } from "@/data/fixture-catalogue";
import type { CatalogueRepository } from "@/repositories/catalogue-repository";
import { resolveModelSegment } from "@/app/en-ae/market/data";

describe("resolveModelSegment", () => {
  it("resolves a model from the complete API catalogue before loading insights", async () => {
    const target = fixtureCatalogue.find((listing) => listing.make === "BMW" && listing.model === "X5")!;
    const getAll = vi.fn(async () => [target]);
    const getModelSummary = vi.fn(async () => ({
      make: target.make,
      model: target.model,
      activeListings: 1,
      medianPrice: target.price,
      minPrice: target.price,
      maxPrice: target.price,
      minMileage: target.mileageKm,
      maxMileage: target.mileageKm,
      lastUpdatedAt: target.lastSeenAt,
    }));
    const repository = { getAll, getModelSummary } as unknown as CatalogueRepository;

    const segment = await resolveModelSegment("bmw", "x5", repository);

    expect(segment?.first.id).toBe(target.id);
    expect(getAll).toHaveBeenCalledOnce();
    expect(getModelSummary).toHaveBeenCalledWith("BMW", "X5");
  });
});
