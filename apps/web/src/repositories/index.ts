import { fixtureCatalogue } from "@/data/fixture-catalogue";
import { FixtureCatalogueRepository } from "@/repositories/fixture-catalogue-repository";

export const catalogueRepository = new FixtureCatalogueRepository(fixtureCatalogue);
