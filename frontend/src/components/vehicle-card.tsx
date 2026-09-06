import Image from "next/image";
import Link from "next/link";
import type { Route } from "next";
import { ArrowUpRight, Gauge, MapPin } from "lucide-react";
import type { Listing } from "@/domain/schemas";
import { DealPosition } from "@/components/deal-position";
import { CompareButton } from "@/components/compare-button";
import { ShortlistButton } from "@/components/shortlist-button";
import { cn } from "@/lib/utils";

export function VehicleCard({ listing, returnHref, priority = false, layout = "grid" }: {
  listing: Listing; returnHref?: string; priority?: boolean; layout?: "grid" | "list";
}) {
  const detailHref = `/en-ae/cars/${listing.id}${returnHref ? `?from=${encodeURIComponent(returnHref)}` : ""}` as Route;
  return (
    <article className={cn("vehicle-card group min-w-0 overflow-hidden border border-border bg-card", layout === "list" && "md:grid md:grid-cols-[minmax(220px,0.85fr)_1.15fr]")}>
      <Link href={detailHref} aria-label={`View ${listing.title}`} className="relative block aspect-[4/3] overflow-hidden bg-carbon">
        <Image src={listing.photos[0]} alt={listing.title} fill priority={priority} sizes="(max-width: 768px) 100vw, 33vw" className="vehicle-card-image object-cover" />
        <span className="absolute left-3 top-3 border border-white/20 bg-obsidian/85 px-2.5 py-1.5 text-[11px] font-semibold tracking-wide text-white">{listing.specifications} specs</span>
        {listing.source.status === "Fixture" && <span className="absolute bottom-3 left-3 bg-obsidian/85 px-2 py-1 text-[10px] font-medium text-white">Illustrative listing</span>}
        <span aria-hidden="true" className="absolute bottom-3 right-3 flex size-8 items-center justify-center bg-white text-obsidian"><ArrowUpRight className="size-4" /></span>
      </Link>
      <div className="flex min-w-0 flex-col p-5">
        <p className="text-[11px] font-medium tracking-wide text-muted-foreground">{listing.year} <span className="mx-1 text-border">/</span> {listing.trim}</p>
        <h3 className="mt-1 text-lg font-semibold leading-snug tracking-tight">{listing.make} {listing.model}</h3>
        <p className="mt-4 flex flex-wrap items-baseline gap-x-2 tabular-nums"><span className="text-xs font-medium text-muted-foreground">AED</span><span className="text-[28px] font-semibold leading-none tracking-tight">{listing.price.toLocaleString("en-AE")}</span></p>
        <div className="mt-3 min-h-6"><DealPosition position={listing.dealPosition} compact /></div>
        <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 border-t border-border pt-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5"><Gauge aria-hidden="true" className="size-3.5" />{listing.mileageKm.toLocaleString("en-AE")} km</span>
          <span className="flex items-center gap-1.5"><MapPin aria-hidden="true" className="size-3.5" />{listing.city}</span>
        </div>
        <div className="mt-auto flex items-center gap-2 pt-5"><CompareButton listingId={listing.id} /><ShortlistButton listingId={listing.id} className="ml-auto" /></div>
      </div>
    </article>
  );
}
