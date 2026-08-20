import { fixtureCatalogue } from "@/data/fixture-catalogue";
import { FixtureCatalogueRepository } from "@/repositories/fixture-catalogue-repository";
import { ApiCatalogueRepository } from "@/repositories/api-catalogue-repository";

type CatalogueEnvironment = Readonly<Record<string, string | undefined>>;

export function createCatalogueRepository(environment: CatalogueEnvironment = process.env) {
  const source = environment.CARVEO_CATALOGUE_SOURCE ?? "api";
  const apiUrl = environment.CARVEO_API_INTERNAL_URL ?? "http://localhost:8000";

  return source === "fixture"
    ? new FixtureCatalogueRepository(fixtureCatalogue)
    : new ApiCatalogueRepository(apiUrl);
}

export const catalogueRepository = createCatalogueRepository();
