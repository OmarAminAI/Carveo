"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PriceObservation } from "@/domain/schemas";

export function PriceHistoryChart({ data }: { data: PriceObservation[] }) {
  const formatted = data.map((item) => ({ ...item, date: new Intl.DateTimeFormat("en-AE", { month: "short", day: "numeric" }).format(new Date(item.observedAt)) }));
  return <div className="h-64 w-full" aria-label="Price history chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={formatted} margin={{ top: 12, right: 12, bottom: 0, left: 0 }}><CartesianGrid stroke="#d5d5d0" vertical={false} /><XAxis dataKey="date" tickLine={false} axisLine={false} fontSize={12} /><YAxis tickFormatter={(value) => `${Math.round(value / 1000)}k`} tickLine={false} axisLine={false} fontSize={12} width={42} /><Tooltip formatter={(value) => [`AED ${Number(value).toLocaleString("en-AE")}`, "Price"]} /><Line type="monotone" dataKey="price" stroke="#0b0b0c" strokeWidth={2} dot={{ fill: "#ffc000", stroke: "#0b0b0c", strokeWidth: 2, r: 4 }} isAnimationActive={false} /></LineChart></ResponsiveContainer></div>;
}
