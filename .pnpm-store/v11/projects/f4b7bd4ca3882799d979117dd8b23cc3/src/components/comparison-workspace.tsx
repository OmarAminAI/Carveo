"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";
import type { Listing } from "@/domain/schemas";
import { useProfile } from "@/profile/profile-provider";

type ComparisonRow = { group: string; label: string; values: string[]; different: boolean };
const money = (value: number) => `AED ${value.toLocaleString("en-AE")}`;

export function buildComparisonRows(listings: Listing[]): ComparisonRow[] {
  const definitions: Array<[string, string, (listing: Listing) => string]> = [
    ["Identity", "Make", (listing) => listing.make],
    ["Identity", "Model", (listing) => listing.model],
    ["Identity", "Year", (listing) => String(listing.year)],
    ["Identity", "Trim", (listing) => listing.trim],
    ["Value", "Price", (listing) => money(listing.price)],
    ["Value", "Typical position", (listing) => listing.dealPosition?.label ?? "Limited data"],
    ["Use", "Mileage", (listing) => `${listing.mileageKm.toLocaleString("en-AE")} km`],
    ["Use", "Body type", (listing) => listing.bodyType],
    ["Use", "City", (listing) => listing.city],
    ["Evidence", "Specifications", (listing) => listing.specifications],
    ["Evidence", "Condition", (listing) => listing.conditionEvidence.find((item) => item.kind !== "unknown")?.label ?? "Condition not stated"],
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
  const [mobileId, setMobileId] = useState(ids[0] ?? "");
  const rows = useMemo(() => buildComparisonRows(listings).filter((row) => !differencesOnly || row.different), [differencesOnly, listings]);
  const remove = (id: string) => {
    removeComparison(id);
    const next = ids.filter((candidate) => candidate !== id);
    const params = new URLSearchParams();
    next.forEach((candidate) => params.append("id", candidate));
    router.replace(`/en-ae/compare${next.length ? `?${params}` : ""}` as Route);
  };
  if (!hydrated && !requestedIds.length) return <p className="py-16 text-sm text-muted-foreground">Loading local comparison...</p>;
  if (!listings.length) return <div className="border border-border bg-white p-8"><h2 className="font-display text-3xl font-semibold uppercase">No cars selected</h2><p className="mt-2 text-sm text-muted-foreground">Add two to four cars from the catalogue to compare factual listing details.</p></div>;
  const mobileListing = listings.find((listing) => listing.id === mobileId) ?? listings[0];
  const mobileIndex = listings.indexOf(mobileListing);
  return <div><div className="mb-5 flex flex-wrap items-center justify-between gap-4"><p className="text-sm text-muted-foreground">{listings.length} of 4 vehicles</p><label className="flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={differencesOnly} onChange={(event) => setDifferencesOnly(event.target.checked)} />Differences only</label></div><div className="md:hidden"><label className="text-xs font-semibold uppercase" htmlFor="mobile-car">Vehicle</label><select id="mobile-car" className="mt-2 h-11 w-full border border-border bg-white px-3" value={mobileListing.id} onChange={(event) => setMobileId(event.target.value)}>{listings.map((listing) => <option key={listing.id} value={listing.id}>{listing.year} {listing.make} {listing.model}</option>)}</select><div className="mt-4 border border-border bg-white p-4"><div className="relative aspect-[4/3]"><Image src={mobileListing.photos[0]} alt={mobileListing.title} fill sizes="calc(100vw - 64px)" className="object-cover" /></div><button type="button" onClick={() => remove(mobileListing.id)} className="mt-3 inline-flex h-9 items-center gap-2 text-sm font-semibold"><X className="size-4" />Remove vehicle</button><dl className="mt-2">{rows.map((row) => <div key={`${row.group}-${row.label}`} className="grid grid-cols-[120px_1fr] gap-3 border-t border-border py-3 text-sm"><dt className="text-muted-foreground">{row.label}</dt><dd className="font-medium">{row.values[mobileIndex]}</dd></div>)}</dl></div></div><div className="hidden overflow-x-auto border border-border bg-white md:block"><table className="w-full min-w-[760px] border-collapse text-left text-sm"><thead><tr><th className="sticky left-0 z-20 w-44 bg-white p-4">Attribute</th>{listings.map((listing) => <th key={listing.id} className="min-w-52 border-l border-border p-4 align-top"><div className="relative aspect-[4/3]"><Image src={listing.photos[0]} alt={listing.title} fill sizes="208px" className="object-cover" /></div><p className="mt-3 font-semibold">{listing.year} {listing.make} {listing.model}</p><button type="button" onClick={() => remove(listing.id)} className="mt-2 inline-flex items-center gap-1 text-xs"><X className="size-3" />Remove</button></th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.group}-${row.label}`} className="border-t border-border"><th className="sticky left-0 z-10 bg-white p-4 font-medium">{index === 0 || rows[index - 1]?.group !== row.group ? <span className="mb-1 block text-[10px] font-semibold uppercase text-muted-foreground">{row.group}</span> : null}{row.label}</th>{row.values.map((value, valueIndex) => <td key={`${row.label}-${ids[valueIndex]}`} className={`border-l border-border p-4 ${row.different ? "font-semibold" : ""}`}>{value}</td>)}</tr>)}</tbody></table></div></div>;
}
