import type { Metadata } from "next";
import { ShortlistWorkspace } from "@/components/shortlist-workspace";
import { catalogueRepository } from "@/repositories";

export const metadata: Metadata = { title: "Buyer workspace", description: "Your browser-local Carveo shortlist, searches, comparison, and recent views." };

export default async function ShortlistPage() {
  const allListings = await catalogueRepository.getAll();
  return <main className="min-h-screen bg-marble py-10"><div className="shell"><p className="text-xs font-semibold uppercase text-muted-foreground">Anonymous profile</p><h1 className="font-display mt-2 text-5xl font-semibold uppercase">Buyer workspace</h1><div className="mt-8"><ShortlistWorkspace allListings={allListings} /></div></div></main>;
}
