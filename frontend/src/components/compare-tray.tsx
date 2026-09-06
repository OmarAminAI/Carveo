"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, X } from "lucide-react";
import type { Listing } from "@/domain/schemas";
import { useProfile } from "@/profile/profile-provider";
import { CompareButton } from "@/components/compare-button";
import { ShortlistButton } from "@/components/shortlist-button";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const noListings: Listing[] = [];

export function CompareTray({ listings = noListings, detailListing }: { listings?: Listing[]; detailListing?: Listing }) {
  const { profile, removeComparison } = useProfile();
  const [names, setNames] = useState<Record<string, string>>({});
  useEffect(() => {
    setNames((current) => ({ ...current, ...Object.fromEntries(listings.map((listing) => [listing.id, `${listing.year} ${listing.make} ${listing.model}`])) }));
  }, [listings]);
  if (!profile.compareIds.length && !detailListing) return null;
  const query = new URLSearchParams();
  profile.compareIds.forEach((id) => query.append("id", id));

  return <aside aria-label="Selected cars" className={cn("compare-tray fixed inset-x-0 bottom-0 z-40 border-t border-white/15 bg-obsidian text-white shadow-[0_-8px_32px_#00000014]", !profile.compareIds.length && "lg:hidden")}>
    <div className="shell py-3">
      {detailListing && <div className={cn("flex flex-wrap items-center justify-between gap-2 lg:hidden", profile.compareIds.length && "mb-3 border-b border-white/20 pb-3")}>
        <p className="text-base font-semibold tabular-nums"><span className="mr-1 text-[10px] text-white/60">AED</span>{detailListing.price.toLocaleString("en-AE")}</p>
        <div className="flex gap-2 text-obsidian"><CompareButton listingId={detailListing.id} /><ShortlistButton listingId={detailListing.id} /></div>
      </div>}
      {profile.compareIds.length > 0 && <>
        <div className="flex items-center justify-between gap-3">
          <div><p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">Your comparison</p><p role="status" className="mt-1 text-sm font-medium">{profile.compareIds.length} of 4 cars selected</p></div>
          <Link href={`/en-ae/compare?${query}`} className={cn(buttonVariants({ variant: "signal", size: "sm" }), "min-h-10 border-signal")}>Compare now <ArrowRight className="size-4" /></Link>
        </div>
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1" aria-label="Cars in comparison">
          {profile.compareIds.map((id, index) => {
            const listing = listings.find((item) => item.id === id);
            const name = listing ? `${listing.year} ${listing.make} ${listing.model}` : names[id] ?? `Selected car ${index + 1} · ${id}`;
            return <button key={id} type="button" aria-label={`Remove ${name} from comparison`} onClick={() => removeComparison(id)} className="inline-flex min-h-10 shrink-0 items-center gap-3 border border-white/20 bg-white/5 px-3 text-xs transition-colors hover:bg-white/15"><span className="max-w-48 truncate">{name}</span><X aria-hidden="true" className="size-3.5 shrink-0 text-white/60" /></button>;
          })}
        </div>
      </>}
    </div>
  </aside>;
}
