import Image from "next/image";
import Link from "next/link";
import type { Route } from "next";
import { Gauge, MapPin } from "lucide-react";
import type { Listing } from "@/domain/schemas";
import { DealPosition } from "@/components/deal-position";
import { CompareButton } from "@/components/compare-button";
import { ShortlistButton } from "@/components/shortlist-button";

export function VehicleCard({ listing, returnHref, priority = false }: { listing: Listing; returnHref?: string; priority?: boolean }) {
  const evidence = listing.conditionEvidence[0];
  const detailHref = `/en-ae/cars/${listing.id}${returnHref ? `?from=${encodeURIComponent(returnHref)}` : ""}` as Route;
  return (
    <article className="group border border-border bg-card">
      <Link href={detailHref} aria-label={`View ${listing.title}`} className="relative block aspect-[4/3] overflow-hidden bg-carbon">
        <Image src={listing.photos[0]} alt={listing.title} fill priority={priority} sizes="(max-width: 768px) 100vw, 33vw" className="object-cover transition-transform duration-200 group-hover:scale-[1.02]" />
        <span className="absolute left-3 top-3 bg-obsidian px-2 py-1 text-xs font-semibold text-white">{listing.specifications} specs</span>
      </Link>
      <div className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div><p className="text-xs text-muted-foreground">{listing.year} · {listing.trim}</p><h3 className="mt-1 text-base font-semibold leading-tight">{listing.make} {listing.model}</h3></div>
          <p className="shrink-0 text-right text-lg font-bold">AED {listing.price.toLocaleString("en-AE")}</p>
        </div>
        <div className="my-4"><DealPosition position={listing.dealPosition} /></div>
        <div className="grid grid-cols-2 gap-2 border-y border-border py-3 text-xs">
          <div className="flex items-center gap-2"><Gauge className="size-4 text-steel" /><span>{listing.mileageKm.toLocaleString("en-AE")} km</span></div>
          <div className="flex items-center gap-2"><MapPin className="size-4 text-steel" /><span>{listing.city}</span></div>
        </div>
        <div className="mt-3 flex items-end justify-between gap-3 text-xs"><div><p className={evidence.kind === "warning" ? "font-semibold text-destructive" : "font-semibold"}>{evidence.label}</p><p className="mt-1 text-muted-foreground">{listing.source.name}</p></div><span className="text-muted-foreground">Fixture</span></div>
        <div className="mt-4 flex items-center gap-2"><CompareButton listingId={listing.id} /><ShortlistButton listingId={listing.id} className="ml-auto" /></div>
      </div>
    </article>
  );
}
