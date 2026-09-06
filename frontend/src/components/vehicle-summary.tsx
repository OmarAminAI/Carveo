import { ExternalLink, Gauge, MapPin } from "lucide-react";
import type { Listing } from "@/domain/schemas";
import { CompareButton } from "@/components/compare-button";
import { ShortlistButton } from "@/components/shortlist-button";
import { DealPosition } from "@/components/deal-position";
import { buttonVariants } from "@/components/ui/button";

export function VehicleSummary({ listing }: { listing: Listing }) {
  const fixture = listing.source.status === "Fixture";
  return <aside className="border border-border bg-white p-6 lg:sticky lg:top-20 lg:p-8">
    <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">{listing.year} / {listing.specifications} specs</p>
    <h1 className="font-display mt-3 text-5xl font-semibold uppercase leading-[0.95]">{listing.make}<br />{listing.model}</h1>
    <p className="mt-3 text-sm text-muted-foreground">{listing.trim}</p>
    <p className="mt-7 flex flex-wrap items-baseline gap-2"><span className="text-xs text-muted-foreground">AED</span><span className="text-4xl font-semibold tracking-tight tabular-nums">{listing.price.toLocaleString("en-AE")}</span></p>
    <div className="mt-4"><DealPosition position={listing.dealPosition} /></div>
    <div className="my-6 grid grid-cols-2 gap-3 border-y border-border py-5 text-sm">
      <span><Gauge aria-hidden="true" className="mb-2 size-4 text-muted-foreground" />{listing.mileageKm.toLocaleString("en-AE")} km</span>
      <span><MapPin aria-hidden="true" className="mb-2 size-4 text-muted-foreground" />{listing.city}</span>
    </div>
    <div className="hidden gap-2 lg:flex"><CompareButton listingId={listing.id} /><ShortlistButton listingId={listing.id} /></div>
    <a href={listing.source.listingUrl} target="_blank" rel="noreferrer" className={`${buttonVariants({ variant: "signal" })} mt-3 w-full`}>{fixture ? "Open illustrative source" : "View seller listing"}<ExternalLink className="size-4" /></a>
    <p className="mt-4 text-xs leading-relaxed text-muted-foreground">{fixture ? "Illustrative listing, not a live advertisement. " : ""}Carveo does not inspect vehicles or guarantee seller claims.</p>
  </aside>;
}
