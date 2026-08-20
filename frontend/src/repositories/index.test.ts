import { describe, expect, it } from "vitest";
import { ApiCatalogueRepository } from "@/repositories/api-catalogue-repository";
import { FixtureCatalogueRepository } from "@/repositories/fixture-catalogue-repository";
import { createCatalogueRepository } from "@/repositories";

describe("createCatalogueRepository", () => {
  it("uses the API unless fixture mode is explicitly requested", () => {
    expect(createCatalogueRepository({})).toBeInstanceOf(ApiCatalogueRepository);
    expect(createCatalogueRepository({ CARVEO_CATALOGUE_SOURCE: "fixture" })).toBeInstanceOf(
      FixtureCatalogueRepository,
    );
  });
});
