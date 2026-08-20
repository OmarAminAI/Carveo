import { slugifyVehicleName } from "@/domain/query";
import type { CatalogueRepository } from "@/repositories/catalogue-repository";

export async function resolveModelSegment(
  makeSlug: string,
  modelSlug: string,
  repository: CatalogueRepository,
) {
  const all = await repository.getAll();
  const first = all.find(
    (listing) =>
      slugifyVehicleName(listing.make) === makeSlug &&
      slugifyVehicleName(listing.model) === modelSlug,
  );
  if (!first) return null;

  const summary = await repository.getModelSummary(first.make, first.model);
  if (!summary) return null;

  return {
    first,
    summary,
    listings: all.filter(
      (listing) => listing.make === first.make && listing.model === first.model,
    ),
  };
}
