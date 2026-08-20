import type { Metadata } from "next";
import Link from "next/link";
import { Grid2X2, List } from "lucide-react";
import { CompareTray } from "@/components/compare-tray";
import { EmptyState } from "@/components/empty-state";
import { FilterFields } from "@/components/filter-fields";
import { MobileFilterDrawer } from "@/components/mobile-filter-drawer";
import { SaveSearchButton } from "@/components/save-search-button";
import { VehicleCard } from "@/components/vehicle-card";
import { parseListingQuery, toListingSearchParams } from "@/domain/query";
import { catalogueRepository } from "@/repositories";

export const metadata: Metadata = { title: "Used cars in the UAE", description: "Browse and compare fixture-powered UAE used-car listings." };

function toParams(values: Record<string, string | string[] | undefined>) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (Array.isArray(value)) value.forEach((item) => params.append(key, item));
    else if (value !== undefined) params.set(key, value);
  }
  return params;
}

export default async function CarsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const raw = await searchParams;
  const query = parseListingQuery(toParams(raw));
  const results = await catalogueRepository.search(query);
  const view = raw.view === "list" ? "list" : "grid";
  const gridParams = toListingSearchParams(query); gridParams.set("view", "grid");
  const listParams = toListingSearchParams(query); listParams.set("view", "list");
  const savedQuery = toListingSearchParams(query).toString();
  const searchLabel = query.make.length ? `${query.make.join(", ")} search` : query.bodyType.length ? `${query.bodyType.join(", ")} search` : "UAE car search";
  const currentParams = toParams(raw).toString();
  const returnHref = `/en-ae/cars${currentParams ? `?${currentParams}` : ""}`;

  return <main className="min-h-screen bg-marble pb-28">
    <section className="border-b border-border bg-white py-8"><div className="shell"><p className="text-xs font-semibold uppercase text-muted-foreground">English · UAE</p><h1 className="font-display mt-2 text-5xl font-semibold uppercase">Cars for sale</h1><p className="mt-2 text-sm text-muted-foreground">{results.total} fixture listings · last refreshed 19 Aug 2026</p></div></section>
    <div className="shell py-6">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <MobileFilterDrawer query={query} />
        <SaveSearchButton query={savedQuery} label={searchLabel} />
        <form action="/en-ae/cars" className="ml-auto flex items-center gap-2">
          {[...toListingSearchParams(query)].filter(([key]) => key !== "sort" && key !== "page").map(([key, value], index) => <input key={`${key}-${value}-${index}`} type="hidden" name={key} value={value} />)}
          <label className="text-xs font-semibold uppercase" htmlFor="sort">Sort</label>
          <select id="sort" name="sort" defaultValue={query.sort} className="h-10 border border-border bg-white px-3 text-sm"><option value="best-match">Best match</option><option value="best-deal">Best deal</option><option value="newest">Newest</option><option value="lowest-price">Lowest price</option><option value="lowest-mileage">Lowest mileage</option></select>
          <button className="h-10 border border-obsidian bg-obsidian px-4 text-sm font-semibold text-white">Apply</button>
        </form>
        <div className="flex border border-border bg-white"><Link href={`/en-ae/cars?${gridParams}`} aria-label="Grid view" className={`inline-flex size-10 items-center justify-center ${view === "grid" ? "bg-obsidian text-white" : ""}`}><Grid2X2 className="size-4" /></Link><Link href={`/en-ae/cars?${listParams}`} aria-label="List view" className={`inline-flex size-10 items-center justify-center ${view === "list" ? "bg-obsidian text-white" : ""}`}><List className="size-4" /></Link></div>
      </div>
      <div className="grid items-start gap-6 lg:grid-cols-[248px_minmax(0,1fr)]">
        <aside className="sticky top-20 hidden border border-border bg-white p-5 lg:block"><form action="/en-ae/cars"><FilterFields query={query} /><button className="mt-6 h-10 w-full bg-obsidian text-sm font-semibold text-white">Apply filters</button><Link href="/en-ae/cars" className="mt-2 flex h-10 items-center justify-center text-sm">Reset</Link></form></aside>
        <section>{results.items.length ? <div className={view === "list" ? "grid gap-4 md:grid-cols-2" : "grid gap-4 md:grid-cols-2 xl:grid-cols-3"}>{results.items.map((listing, index) => <VehicleCard key={listing.id} listing={listing} returnHref={returnHref} priority={index === 0} />)}</div> : <EmptyState />}{results.pageCount > 1 && <nav aria-label="Pagination" className="mt-8 flex flex-wrap gap-2">{Array.from({ length: results.pageCount }, (_, index) => { const params = toListingSearchParams({ ...query, page: index + 1 }); return <Link key={index} href={`/en-ae/cars?${params}`} className={`inline-flex size-10 items-center justify-center border ${results.page === index + 1 ? "border-obsidian bg-obsidian text-white" : "border-border bg-white"}`}>{index + 1}</Link>; })}</nav>}</section>
      </div>
    </div>
    <CompareTray />
  </main>;
}
