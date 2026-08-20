import Image from "next/image";
import Link from "next/link";
import { ArrowRight, BarChart3, Database, ShieldQuestion } from "lucide-react";
import { SearchConsole } from "@/components/search-console";
import { VehicleCard } from "@/components/vehicle-card";
import { catalogueRepository } from "@/repositories";
import { parseListingQuery } from "@/domain/query";

const bodyTypes = ["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"] as const;
const makeLinks = ["Toyota", "Nissan", "Mercedes-Benz", "BMW", "Porsche", "Ford", "Volkswagen", "Lexus"];

export default async function HomePage() {
  const base = parseListingQuery(new URLSearchParams());
  const deals = await catalogueRepository.search({ ...base, sort: "best-deal", pageSize: 12 });
  const recent = await catalogueRepository.search({ ...base, sort: "newest", pageSize: 12 });
  return (
    <main>
      <section className="relative min-h-[calc(92svh-64px)] overflow-hidden bg-obsidian text-white">
        <Image src="/media/fixture-suv.jpg" alt="Modern SUV in a mountain landscape" fill priority sizes="100vw" className="object-cover" />
        <div className="absolute inset-0 bg-black/55" />
        <div className="shell relative flex min-h-[calc(92svh-64px)] flex-col justify-end pb-8 pt-12 md:pb-14 md:pt-20">
          <p className="mb-4 text-sm font-semibold uppercase text-signal">UAE used-car intelligence</p>
          <h1 className="font-display max-w-4xl text-6xl font-semibold uppercase leading-[0.9] sm:text-7xl lg:text-8xl">Find the right car.<br />Know the market.</h1>
          <p className="mt-5 max-w-xl text-base text-white/75 md:text-lg">Search clear fixture inventory, compare typical prices, and keep unknown condition claims visible.</p>
          <div className="mt-8 max-w-5xl"><SearchConsole /></div>
        </div>
      </section>

      <section className="border-b border-border bg-white py-14">
        <div className="shell">
          <div className="flex items-end justify-between gap-6"><div><p className="text-xs font-semibold uppercase text-muted-foreground">Start with shape</p><h2 className="font-display mt-2 text-4xl font-semibold uppercase">Browse by body type</h2></div><Link href="/en-ae/cars" className="hidden items-center gap-2 text-sm font-semibold md:flex">View all <ArrowRight className="size-4" /></Link></div>
          <div className="mt-8 grid grid-cols-2 gap-2 md:grid-cols-3 lg:grid-cols-6">
            {bodyTypes.map((bodyType) => <Link key={bodyType} href={`/en-ae/cars?bodyType=${bodyType}`} className="group relative aspect-[4/3] overflow-hidden bg-carbon"><Image src={`/media/fixture-${bodyType.toLowerCase()}.jpg`} alt={`${bodyType} vehicles`} fill sizes="(max-width:768px) 50vw, 16vw" className="object-cover transition-transform duration-200 group-hover:scale-[1.03]" /><span className="absolute inset-x-0 bottom-0 bg-obsidian/85 p-3 font-semibold text-white">{bodyType}</span></Link>)}
          </div>
          <div className="mt-8 flex flex-wrap gap-2">{makeLinks.map((make) => <Link key={make} href={`/en-ae/cars?make=${encodeURIComponent(make)}`} className="border border-border px-4 py-2 text-sm font-medium hover:border-obsidian hover:bg-obsidian hover:text-white">{make}</Link>)}</div>
        </div>
      </section>

      <section className="bg-marble py-16"><div className="shell"><div className="flex items-end justify-between"><div><p className="text-xs font-semibold uppercase text-muted-foreground">Price position first</p><h2 className="font-display mt-2 text-4xl font-semibold uppercase">Potentially strong deals</h2></div><Link href="/en-ae/cars?sort=best-deal" className="text-sm font-semibold">See all deals</Link></div><div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">{deals.items.slice(0, 4).map((listing) => <VehicleCard key={listing.id} listing={listing} />)}</div></div></section>

      <section className="grid bg-carbon text-white lg:grid-cols-3">
        <div className="border-b border-white/15 p-8 lg:border-b-0 lg:border-r"><BarChart3 className="size-6 text-signal" /><h2 className="font-display mt-12 text-3xl font-semibold uppercase">Typical price, explained</h2><p className="mt-3 text-sm text-white/60">Medians use comparable fixture listings. Every label shows its sample size and declines to score sparse data.</p></div>
        <div className="border-b border-white/15 p-8 lg:border-b-0 lg:border-r"><Database className="size-6 text-signal" /><h2 className="font-display mt-12 text-3xl font-semibold uppercase">Source stays visible</h2><p className="mt-3 text-sm text-white/60">Every record identifies its fixture source. Live inventory remains gated until a source is formally authorized.</p></div>
        <div className="p-8"><ShieldQuestion className="size-6 text-signal" /><h2 className="font-display mt-12 text-3xl font-semibold uppercase">Unknown means unknown</h2><p className="mt-3 text-sm text-white/60">Missing accident, service, or inspection evidence is never relabelled as clean or verified.</p></div>
      </section>

      <section className="bg-white py-16"><div className="shell"><div className="flex items-end justify-between"><div><p className="text-xs font-semibold uppercase text-muted-foreground">Fresh fixture inventory</p><h2 className="font-display mt-2 text-4xl font-semibold uppercase">Recently added</h2></div><Link href="/en-ae/cars?sort=newest" className="text-sm font-semibold">Browse newest</Link></div><div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">{recent.items.slice(0, 4).map((listing) => <VehicleCard key={listing.id} listing={listing} />)}</div></div></section>
    </main>
  );
}
