import type { Metadata } from "next";
import type { Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { CompareTray } from "@/components/compare-tray";
import { ConditionEvidencePanel } from "@/components/condition-evidence";
import { VehicleSummary } from "@/components/vehicle-summary";
import { PriceHistoryChart } from "@/components/price-history-chart";
import { RecentViewRecorder } from "@/components/recent-view-recorder";

import { VehicleCard } from "@/components/vehicle-card";
import { VehicleGallery } from "@/components/vehicle-gallery";

import { catalogueRepository } from "@/repositories";

export async function generateMetadata({ params }: { params: Promise<{ listingId: string }> }): Promise<Metadata> {
  const listing = await catalogueRepository.getById((await params).listingId);
  return listing ? { title: listing.title, description: listing.description } : { title: "Listing not found" };
}
export default async function ListingPage({ params, searchParams }: { params: Promise<{ listingId: string }>; searchParams: Promise<{ from?: string }> }) {
  const { listingId } = await params;
  const listing = await catalogueRepository.getById(listingId);
  if (!listing) notFound();
  const related = await catalogueRepository.getRelated(listingId, 4);
  const from = (await searchParams).from;
  const returnHref = (from?.startsWith("/en-ae/cars") ? from : "/en-ae/cars") as Route;

  return <main className="bg-marble pb-64 lg:pb-40">
    <RecentViewRecorder listingId={listing.id} />
    <div className="shell py-5"><Link href={returnHref} className="inline-flex items-center gap-2 text-sm font-semibold"><ArrowLeft className="size-4" />Back to results</Link></div>
    <div className="shell grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div><VehicleGallery photos={listing.photos} title={listing.title} /></div>
      <VehicleSummary listing={listing} />
      <section className="border border-border bg-white p-6"><p className="text-xs font-semibold uppercase text-muted-foreground">Price history</p><h2 className="font-display mt-2 text-3xl font-semibold uppercase">Price over time</h2><PriceHistoryChart data={listing.priceHistory} /></section>
    </div>
    <section className="shell py-14"><p className="text-xs font-semibold uppercase text-muted-foreground">Condition and ownership</p><h2 className="font-display mt-2 text-4xl font-semibold uppercase">Source-stated evidence</h2><div className="mt-6"><ConditionEvidencePanel evidence={listing.conditionEvidence} /></div></section>
    <section className="shell grid gap-6 border-t border-border py-12 lg:grid-cols-2"><div><h2 className="font-display text-3xl font-semibold uppercase">Specifications</h2><dl className="mt-5 grid grid-cols-2 border-t border-border text-sm">{[["Body type", listing.bodyType], ["Regional specs", listing.specifications], ["Seller", listing.sellerType], ["Source", listing.source.name], ["First seen", new Date(listing.firstSeenAt).toLocaleDateString("en-AE")], ["Last seen", new Date(listing.lastSeenAt).toLocaleDateString("en-AE")]].map(([key, value]) => <div key={key} className="border-b border-border py-4"><dt className="text-xs text-muted-foreground">{key}</dt><dd className="mt-1 font-medium">{value}</dd></div>)}</dl></div><div><h2 className="font-display text-3xl font-semibold uppercase">Features stated</h2><ul className="mt-5 grid grid-cols-2 gap-2">{listing.features.map((feature) => <li key={feature} className="border border-border bg-white p-3 text-sm">{feature}</li>)}</ul>{listing.duplicateOffers.length > 0 && <div className="mt-6"><h3 className="text-sm font-semibold">Duplicate source offers</h3>{listing.duplicateOffers.map((offer) => <p key={offer.url} className="mt-2 text-sm">{offer.source} · AED {offer.price.toLocaleString("en-AE")}</p>)}</div>}</div></section>
    <section className="shell"><h2 className="font-display text-4xl font-semibold uppercase">Related cars</h2><div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">{related.map((item) => <VehicleCard key={item.id} listing={item} />)}</div></section>
    <CompareTray listings={[listing, ...related]} detailListing={listing} />
  </main>;
}
