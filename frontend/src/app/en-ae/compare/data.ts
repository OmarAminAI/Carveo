import type { Listing } from "@/domain/schemas";
import type { CatalogueRepository } from "@/repositories/catalogue-repository";

export async function loadComparisonListings(
  requestedIds: string[],
  repository: CatalogueRepository,
): Promise<Listing[]> {
  return requestedIds.length ? repository.compare(requestedIds) : repository.getAll();
}
