import { fixtureCatalogue } from "@/data/fixture-catalogue";
import { FixtureCatalogueRepository } from "@/repositories/fixture-catalogue-repository";
import { ApiCatalogueRepository } from "@/repositories/api-catalogue-repository";

const source = process.env.CARVEO_CATALOGUE_SOURCE ?? (process.env.NODE_ENV === "development" ? "api" : "fixture");
const apiUrl = process.env.CARVEO_API_INTERNAL_URL ?? "http://localhost:8000";

export const catalogueRepository = source === "api"
  ? new ApiCatalogueRepository(apiUrl)
  : new FixtureCatalogueRepository(fixtureCatalogue);
