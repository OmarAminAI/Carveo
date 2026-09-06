import type { Metadata } from "next";
import { ArrowUpRight, Grid2X2, List, SlidersHorizontal } from "lucide-react";
import { CompareTray } from "@/components/compare-tray";
import { EmptyState } from "@/components/empty-state";
import { BrowseLink, BrowseNavigation, BrowseResults, BrowseSort, FilterForm } from "@/components/browse-navigation";
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
  const gridParams = toParams(raw); gridParams.set("view", "grid");
  const listParams = toParams(raw); listParams.set("view", "list");
  const savedQuery = toListingSearchParams(query).toString();
  const searchLabel = query.make.length ? `${query.make.join(", ")} search` : query.bodyType.length ? `${query.bodyType.join(", ")} search` : "UAE car search";
  const currentParams = toParams(raw).toString();
  const returnHref = `/en-ae/cars${currentParams ? `?${currentParams}` : ""}`;
  const firstResult = (results.page - 1) * query.pageSize + 1;
  const summary = results.total ? `${firstResult}–${Math.min(firstResult + results.items.length - 1, results.total)} of ${results.total} cars` : "No cars match these filters";

  return <main className="min-h-screen bg-marble pb-36">
    <section className="relative overflow-hidden border-b border-white/10 bg-obsidian text-white">
      <div className="shell relative flex items-end justify-between gap-6 py-9 sm:py-12">
        <div className="max-w-2xl"><p className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[.2em] text-signal"><span className="h-1.5 w-1.5 rounded-full bg-signal" />The UAE car edit</p><h1 className="font-display mt-3 text-5xl leading-none font-semibold uppercase sm:text-7xl">Cars for sale</h1><p className="mt-4 max-w-md text-sm leading-relaxed text-white/65 sm:text-base">Find your fit. Compare the details. Choose with confidence.</p><p className="mt-5 text-xs text-white/50">{results.items.some((listing) => listing.source.status === "Fixture") ? "Illustrative inventory · Not live advertisements" : "Source-stated listings across the UAE"}</p></div>
        <div aria-hidden="true" className="hidden size-20 shrink-0 items-center justify-center rounded-full border border-white/20 text-signal sm:flex"><ArrowUpRight className="size-9" strokeWidth={1.5} /></div>
      </div>
    </section>
    <BrowseNavigation>
      <div className="shell py-5 sm:py-7">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-border pb-5">
          <div className="flex items-center gap-2"><MobileFilterDrawer key={currentParams} query={query} currentParams={currentParams} /><SaveSearchButton query={savedQuery} label={searchLabel} /></div>
          <div className="flex w-full min-w-0 items-center justify-between gap-2 sm:ml-auto sm:w-auto sm:gap-4">
            <BrowseSort sort={query.sort} currentParams={currentParams} />
            <div className="flex shrink-0 rounded-lg border border-border bg-white p-0.5"><BrowseLink params={gridParams.toString()} aria-label="Grid view" aria-current={view === "grid" ? "page" : undefined} className={`inline-flex size-10 items-center justify-center rounded-md ${view === "grid" ? "bg-obsidian text-white" : "text-muted-foreground hover:bg-marble"}`}><Grid2X2 className="size-4" /></BrowseLink><BrowseLink params={listParams.toString()} aria-label="List view" aria-current={view === "list" ? "page" : undefined} className={`inline-flex size-10 items-center justify-center rounded-md ${view === "list" ? "bg-obsidian text-white" : "text-muted-foreground hover:bg-marble"}`}><List className="size-4" /></BrowseLink></div>
          </div>
        </div>
        <div className="grid items-start gap-6 lg:grid-cols-[240px_minmax(0,1fr)] xl:gap-8">
          <aside className="hidden border border-border bg-white p-5 lg:block"><div className="mb-5 flex items-center justify-between"><h2 className="font-semibold">Find your fit</h2><SlidersHorizontal className="size-4 text-muted-foreground" /></div><FilterForm key={currentParams} query={query} currentParams={currentParams} /></aside>
          <BrowseResults summary={summary}>
            {results.items.length ? <div className={view === "list" ? "grid gap-4" : "grid gap-4 md:grid-cols-2 xl:grid-cols-3"}>{results.items.map((listing, index) => <VehicleCard key={listing.id} listing={listing} layout={view} returnHref={returnHref} priority={index === 0} />)}</div> : <EmptyState />}
            {results.pageCount > 1 && <nav aria-label="Pagination" className="mt-8 flex flex-wrap gap-2">{Array.from({ length: results.pageCount }, (_, index) => { const params = toParams(raw); params.set("page", String(index + 1)); return <BrowseLink key={index} params={params.toString()} aria-label={`Page ${index + 1}`} aria-current={results.page === index + 1 ? "page" : undefined} className={`inline-flex size-11 items-center justify-center rounded-lg border text-sm font-medium ${results.page === index + 1 ? "border-obsidian bg-obsidian text-white" : "border-border bg-white hover:border-obsidian"}`}>{index + 1}</BrowseLink>; })}</nav>}
          </BrowseResults>
        </div>
      </div>
    </BrowseNavigation>
    <CompareTray listings={results.items} />
  </main>;
}
