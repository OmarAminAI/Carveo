import type { ListingQuery } from "@/domain/schemas";

const options = {
  make: ["Toyota", "Nissan", "Mercedes-Benz", "BMW", "Porsche", "Ford", "Volkswagen", "Lexus"],
  bodyType: ["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"],
  city: ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"],
  specifications: ["GCC", "American", "European", "Japanese"],
  sellerType: ["Dealer", "Private"],
} as const;

export function FilterFields({ query }: { query: ListingQuery }) {
  return <div className="grid gap-6">
    <label className="grid gap-2 text-xs font-semibold uppercase">Keyword<input name="q" defaultValue={query.q} placeholder="Model, trim or city" className="h-11 rounded-lg border border-input bg-white px-3 text-sm font-normal normal-case outline-none focus:border-obsidian" /></label>
    {Object.entries(options).map(([key, values]) => <fieldset key={key} className="border-t border-border pt-4"><legend className="mb-3 text-xs font-semibold uppercase">{key.replace(/([A-Z])/g, " $1")}</legend><div className="grid gap-2">{values.map((value) => <label key={value} className="flex cursor-pointer items-center gap-2.5 py-0.5 text-sm"><input type="checkbox" name={key} value={value} defaultChecked={(query[key as keyof ListingQuery] as string[]).includes(value)} className="size-4 accent-black" />{value}</label>)}</div></fieldset>)}
    <fieldset className="border-t border-border pt-4"><legend className="mb-3 text-xs font-semibold uppercase">Year</legend><div className="grid grid-cols-2 gap-2"><input aria-label="Minimum year" name="yearMin" type="number" defaultValue={query.yearMin} placeholder="From" min="2000" max="2026" className="h-11 min-w-0 rounded-lg border border-input px-3 text-sm" /><input aria-label="Maximum year" name="yearMax" type="number" defaultValue={query.yearMax} placeholder="To" min="2000" max="2026" className="h-11 min-w-0 rounded-lg border border-input px-3 text-sm" /></div></fieldset>
    <fieldset className="border-t border-border pt-4"><legend className="mb-3 text-xs font-semibold uppercase">Price (AED)</legend><div className="grid grid-cols-2 gap-2"><input aria-label="Minimum price in AED" name="priceMin" type="number" defaultValue={query.priceMin} placeholder="Min" min="0" step="5000" className="h-11 min-w-0 rounded-lg border border-input px-3 text-sm" /><input aria-label="Maximum price in AED" name="priceMax" type="number" defaultValue={query.priceMax} placeholder="Max" min="0" step="5000" className="h-11 min-w-0 rounded-lg border border-input px-3 text-sm" /></div></fieldset>
    <label className="grid gap-2 border-t border-border pt-4 text-xs font-semibold uppercase">Maximum mileage<input name="mileageMax" type="number" defaultValue={query.mileageMax} placeholder="Any mileage" min="0" step="5000" className="h-11 rounded-lg border border-input px-3 text-sm font-normal normal-case" /></label>
    <label className="flex items-center gap-2 border-t border-border pt-4 text-sm"><input type="checkbox" name="evidence" value="stated" defaultChecked={query.evidence.includes("stated")} className="size-4 accent-black" />Condition evidence stated</label>
  </div>;
}
