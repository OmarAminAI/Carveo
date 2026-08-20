import type { Metadata } from "next";
import { ComparisonWorkspace } from "@/components/comparison-workspace";
import { loadComparisonListings } from "@/app/en-ae/compare/data";
import { catalogueRepository } from "@/repositories";

export const metadata: Metadata = { title: "Compare cars", description: "Compare two to four UAE fixture listings side by side." };

export default async function ComparePage({ searchParams }: { searchParams: Promise<{ id?: string | string[] }> }) {
  const rawIds = (await searchParams).id;
  const requestedIds = (Array.isArray(rawIds) ? rawIds : rawIds ? [rawIds] : []).slice(0, 4);
  const allListings = await loadComparisonListings(requestedIds, catalogueRepository);
  return <main className="min-h-screen bg-marble py-10"><div className="shell"><p className="text-xs font-semibold uppercase text-muted-foreground">Decision workspace</p><h1 className="font-display mt-2 text-5xl font-semibold uppercase">Compare vehicles</h1><p className="mt-3 max-w-2xl text-sm text-muted-foreground">Compare listing facts and source-stated evidence. Unknown condition information remains unknown.</p><div className="mt-8"><ComparisonWorkspace allListings={allListings} requestedIds={requestedIds} /></div></div></main>;
}
