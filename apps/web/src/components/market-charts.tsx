"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import type { Listing } from "@/domain/schemas";

export function MarketCharts({ listings }: { listings: Listing[] }) {
  const years = [...new Set(listings.map((item) => item.year))].sort();
  const trims = [...new Set(listings.map((item) => item.trim))].sort();
  const specifications = [...new Set(listings.map((item) => item.specifications))].sort();
  const [year, setYear] = useState<number | "all">("all");
  const [trim, setTrim] = useState("all");
  const [specification, setSpecification] = useState("all");
  const filtered = listings.filter((item) =>
    (year === "all" || item.year === year) &&
    (trim === "all" || item.trim === trim) &&
    (specification === "all" || item.specifications === specification),
  );
  const filteredYears = [...new Set(filtered.map((item) => item.year))].sort();
  const distribution = filteredYears.map((item) => {
    const matches = filtered.filter((listing) => listing.year === item);
    return { year: item, median: Math.round(matches.reduce((sum, listing) => sum + listing.price, 0) / matches.length) };
  });

  return <section>
    <div className="mb-6 flex flex-wrap items-end gap-3">
      <MarketSelect id="market-year" label="Model year" value={String(year)} onChange={(value) => setYear(value === "all" ? "all" : Number(value))} options={years.map(String)} allLabel="All years" />
      <MarketSelect id="market-trim" label="Trim" value={trim} onChange={setTrim} options={trims} allLabel="All trims" />
      <MarketSelect id="market-specification" label="Specifications" value={specification} onChange={setSpecification} options={specifications} allLabel="All specifications" />
      <p className="pb-3 text-xs text-muted-foreground">{filtered.length} matching {filtered.length === 1 ? "fixture" : "fixtures"}</p>
    </div>
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="border border-border bg-white p-5"><h3 className="text-sm font-semibold">Price by year</h3><div className="mt-5 h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={distribution}><CartesianGrid stroke="#d5d5d0" vertical={false} /><XAxis dataKey="year" /><YAxis tickFormatter={(value) => `${value / 1000}k`} /><Tooltip /><Bar dataKey="median" fill="#ffc000" isAnimationActive={false} /></BarChart></ResponsiveContainer></div></div>
      <div className="border border-border bg-white p-5"><h3 className="text-sm font-semibold">Mileage versus price</h3><div className="mt-5 h-72"><ResponsiveContainer width="100%" height="100%"><ScatterChart><CartesianGrid stroke="#d5d5d0" /><XAxis type="number" dataKey="mileageKm" name="Mileage" tickFormatter={(value) => `${value / 1000}k`} /><YAxis type="number" dataKey="price" name="Price" tickFormatter={(value) => `${value / 1000}k`} /><Tooltip cursor={{ strokeDasharray: "3 3" }} /><Scatter data={filtered} fill="#0b0b0c" isAnimationActive={false} /></ScatterChart></ResponsiveContainer></div></div>
    </div>
  </section>;
}

function MarketSelect({ id, label, value, onChange, options, allLabel }: { id: string; label: string; value: string; onChange: (value: string) => void; options: string[]; allLabel: string }) {
  return <label className="grid gap-2 text-xs font-semibold uppercase" htmlFor={id}>{label}<select id={id} value={value} onChange={(event) => onChange(event.target.value)} className="h-10 min-w-36 border border-border bg-white px-3 text-sm font-normal normal-case"><option value="all">{allLabel}</option>{options.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>;
}
