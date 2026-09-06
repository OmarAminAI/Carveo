"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowLeftRight, X } from "lucide-react";
import type { Listing } from "@/domain/schemas";
import { useProfile } from "@/profile/profile-provider";

type ComparisonRow = { group: string; label: string; values: string[]; different: boolean };
const money = (value: number) => `AED ${value.toLocaleString("en-AE")}`;

export function buildComparisonRows(listings: Listing[]): ComparisonRow[] {
  const definitions: Array<[string, string, (listing: Listing) => string]> = [
    ["At a glance", "Price", (listing) => money(listing.price)],
    ["At a glance", "Mileage", (listing) => `${listing.mileageKm.toLocaleString("en-AE")} km`],
    ["At a glance", "Year", (listing) => String(listing.year)],
    ["At a glance", "Condition", (listing) => listing.conditionEvidence.find((item) => item.kind === "warning")?.label ?? listing.conditionEvidence.find((item) => item.kind === "positive")?.label ?? "Condition not stated"],
    ["Market context", "Typical position", (listing) => listing.dealPosition?.label ?? "Limited data"],
    ["Vehicle details", "Make", (listing) => listing.make],
    ["Vehicle details", "Model", (listing) => listing.model],
    ["Vehicle details", "Trim", (listing) => listing.trim || "Not stated"],
    ["Vehicle details", "Body type", (listing) => listing.bodyType],
    ["Vehicle details", "Specifications", (listing) => listing.specifications],
    ["Seller and source", "City", (listing) => listing.city],
    ["Seller and source", "Seller", (listing) => listing.sellerType],
    ["Seller and source", "Source", (listing) => listing.source.name],
    ["Seller and source", "Freshness", (listing) => new Date(listing.lastSeenAt).toLocaleDateString("en-AE")],
  ];
  return definitions.map(([group, label, read]) => {
    const values = listings.map(read);
    return { group, label, values, different: new Set(values).size > 1 };
  });
}

export function ComparisonWorkspace({ allListings, requestedIds }: { allListings: Listing[]; requestedIds: string[] }) {
  const router = useRouter();
  const { profile, hydrated, removeComparison } = useProfile();
  const ids = requestedIds.length ? requestedIds.slice(0, 4) : profile.compareIds;
  const listings = ids.map((id) => allListings.find((listing) => listing.id === id)).filter((listing): listing is Listing => Boolean(listing));
  const [differencesOnly, setDifferencesOnly] = useState(false);
  const rows = buildComparisonRows(listings).filter((row) => !differencesOnly || row.different);
  const remove = (id: string) => {
    removeComparison(id);
    const next = ids.filter((candidate) => candidate !== id);
    const params = new URLSearchParams();
    next.forEach((candidate) => params.append("id", candidate));
    router.replace(`/en-ae/compare${next.length ? `?${params}` : ""}` as Route, { scroll: false });
  };
  if (!hydrated && !requestedIds.length) return <p role="status" className="py-16 text-sm text-muted-foreground">Loading your comparison…</p>;
  if (!listings.length) return <div className="border border-border bg-white px-6 py-14 text-center"><ArrowLeftRight className="mx-auto mb-5 size-8 text-muted-foreground" /><h2 className="font-display text-3xl font-semibold uppercase">Your next car starts here</h2><p className="mx-auto mt-3 max-w-sm text-sm text-muted-foreground">Select cars while browsing to see their differences side by side.</p><Link href="/en-ae/cars" className="mt-6 inline-flex min-h-11 items-center gap-2 bg-signal px-5 text-sm font-semibold"><ArrowLeft className="size-4" />Browse cars</Link></div>;
  return <div>
    <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
      <p className="text-sm text-muted-foreground">{listings.length} of 4 vehicles</p>
      <label className="flex min-h-11 cursor-pointer items-center gap-2 border border-border bg-white px-4 text-sm font-medium"><input type="checkbox" className="size-4 accent-black" checked={differencesOnly} onChange={(event) => setDifferencesOnly(event.target.checked)} />Differences only</label>
    </div>
    {listings.length === 1 && <p className="mb-4 border-l-2 border-signal bg-white p-4 text-sm">Add another car to see what sets them apart. <Link href="/en-ae/cars" className="font-semibold underline underline-offset-4">Browse cars</Link></p>}
    {ids.length > listings.length && <p role="status" className="mb-4 text-sm text-muted-foreground">Some selected listings are no longer available.</p>}
    <p className="mb-3 flex items-center gap-2 text-xs text-muted-foreground"><ArrowLeftRight className="size-4" />Scroll sideways to compare. Highlighted rows show differences.</p>
    <div role="region" aria-label="Vehicle comparison" tabIndex={0} className="comparison-scroll overflow-x-auto border border-border bg-white">
      <table className="w-full border-collapse text-left text-sm">
        <caption className="sr-only">Selected vehicles and their listing facts. Highlighted rows have different values.</caption>
        <thead><tr>
          <th scope="col" className="sticky left-0 z-20 w-28 min-w-28 bg-marble p-3 align-bottom text-[10px] font-semibold uppercase tracking-widest md:w-44 md:min-w-44 md:p-5">The details</th>
          {listings.map((listing, index) => <th scope="col" key={listing.id} className="min-w-48 border-l border-border p-3 align-top md:min-w-60 md:p-5">
            <Link href={`/en-ae/cars/${listing.id}` as Route} className="block"><div className="relative aspect-[4/3] overflow-hidden bg-carbon"><Image src={listing.photos[0]} alt={listing.title} fill priority={index === 0} sizes="240px" className="object-cover" /></div><p className="mt-3 text-xs font-normal text-muted-foreground">{listing.year} · {listing.trim}</p><p className="mt-1 text-base font-semibold">{listing.make} {listing.model}</p></Link>
            <button type="button" aria-label={`Remove ${listing.year} ${listing.make} ${listing.model}`} onClick={() => remove(listing.id)} className="mt-2 inline-flex min-h-10 items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground"><X className="size-3.5" />Remove</button>
          </th>)}
        </tr></thead>
        <tbody>{rows.map((row, index) => <tr key={row.label} className={`border-t border-border ${row.different ? "bg-signal/8" : "text-muted-foreground"}`}>
          <th scope="row" className={`sticky left-0 z-10 p-3 text-xs font-medium md:p-5 ${row.different ? "bg-[#fff8e0] text-foreground" : "bg-marble"}`}>
            {index === 0 || rows[index - 1]?.group !== row.group ? <span className="mb-2 block text-[9px] font-semibold uppercase tracking-wider text-muted-foreground">{row.group}</span> : null}
            {row.label}{row.different && <span className="mt-1 block text-[9px] font-normal text-muted-foreground">Differs</span>}
          </th>
          {row.values.map((value, valueIndex) => <td key={listings[valueIndex].id} className={`border-l border-border p-3 md:p-5 ${row.different ? "font-semibold" : ""}`}><span className={row.label === "Price" ? "text-lg tracking-tight tabular-nums" : ""}>{value}</span></td>)}
        </tr>)}</tbody>
      </table>
      {differencesOnly && rows.length === 0 && <p role="status" className="p-6 text-sm text-muted-foreground">No differences in the available listing facts.</p>}
    </div>
  </div>;
}
