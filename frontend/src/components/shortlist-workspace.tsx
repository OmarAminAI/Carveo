"use client";

import { useState } from "react";
import Link from "next/link";
import type { Listing } from "@/domain/schemas";
import { VehicleCard } from "@/components/vehicle-card";
import { useProfile } from "@/profile/profile-provider";

const tabs = ["Shortlisted cars", "Saved search drafts", "Compare set", "Recently viewed"] as const;
type Tab = typeof tabs[number];

export function ShortlistWorkspace({ allListings }: { allListings: Listing[] }) {
  const { profile, hydrated, mode, errorMessage, retrySync } = useProfile();
  const [tab, setTab] = useState<Tab>(tabs[0]);
  const ids = tab === "Shortlisted cars" ? profile.shortlistIds : tab === "Compare set" ? profile.compareIds : profile.recentViewIds;
  const listings = ids.map((id) => allListings.find((listing) => listing.id === id)).filter((listing): listing is Listing => Boolean(listing));
  const storageCopy = mode === "authenticated"
    ? "Synced to your Carveo buyer profile. Recent views remain on this browser."
    : "Stored in this browser until you sign in and merge it with your buyer profile.";
  return <div><div className="overflow-x-auto border-b border-border" role="tablist" aria-label="Buyer workspace"><div className="flex min-w-max">{tabs.map((item) => <button key={item} type="button" role="tab" aria-selected={tab === item} onClick={() => setTab(item)} className={`h-12 border-b-2 px-4 text-sm font-semibold ${tab === item ? "border-signal bg-white" : "border-transparent"}`}>{item}</button>)}</div></div><div className="my-5 flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground"><p>{storageCopy}</p>{mode === "error" ? <div className="flex items-center gap-3"><span>{errorMessage}</span><button type="button" className="font-semibold text-foreground underline" onClick={retrySync}>Retry</button></div> : null}</div>{!hydrated || mode === "loading" ? <p className="py-12 text-sm text-muted-foreground">Loading buyer workspace...</p> : tab === "Saved search drafts" ? profile.savedSearchDrafts.length ? <div className="grid gap-3">{profile.savedSearchDrafts.map((draft) => <Link key={draft.id} href={`/en-ae/cars?${draft.query}`} className="flex items-center justify-between border border-border bg-white p-5"><span><strong className="block">{draft.label}</strong><span className="mt-1 block text-xs text-muted-foreground">Saved {new Date(draft.savedAt).toLocaleDateString("en-AE")}</span></span><span className="text-sm font-semibold">Open search</span></Link>)}</div> : <WorkspaceEmpty label="No saved search drafts" action="Browse and save a useful filter set." /> : listings.length ? <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">{listings.map((listing) => <VehicleCard key={listing.id} listing={listing} />)}</div> : <WorkspaceEmpty label={`No ${tab.toLowerCase()}`} action="Browse the catalogue to start building your buyer workspace." />}</div>;
}

function WorkspaceEmpty({ label, action }: { label: string; action: string }) {
  return <div className="border border-border bg-white p-8"><h2 className="font-display text-3xl font-semibold uppercase">{label}</h2><p className="mt-2 text-sm text-muted-foreground">{action}</p><Link href="/en-ae/cars" className="mt-5 inline-flex h-10 items-center border border-obsidian bg-obsidian px-4 text-sm font-semibold text-white">Browse cars</Link></div>;
}
