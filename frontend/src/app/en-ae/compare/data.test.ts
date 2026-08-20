import { describe, expect, it, vi } from "vitest";
import type { CatalogueRepository } from "@/repositories/catalogue-repository";
import { loadComparisonListings } from "@/app/en-ae/compare/data";

describe("loadComparisonListings", () => {
  it("uses the compare endpoint for shareable listing IDs", async () => {
    const compare = vi.fn(async () => []);
    const getAll = vi.fn(async () => []);
    const repository = { compare, getAll } as unknown as CatalogueRepository;

    await loadComparisonListings(["first", "second"], repository);

    expect(compare).toHaveBeenCalledWith(["first", "second"]);
    expect(getAll).not.toHaveBeenCalled();
  });

  it("loads the catalogue when browser-local comparison IDs are not on the URL", async () => {
    const compare = vi.fn(async () => []);
    const getAll = vi.fn(async () => []);
    const repository = { compare, getAll } as unknown as CatalogueRepository;

    await loadComparisonListings([], repository);

    expect(getAll).toHaveBeenCalledOnce();
    expect(compare).not.toHaveBeenCalled();
  });
});
