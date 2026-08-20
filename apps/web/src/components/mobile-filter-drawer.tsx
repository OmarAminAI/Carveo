"use client";

import { Drawer } from "@base-ui/react/drawer";
import { SlidersHorizontal, X } from "lucide-react";
import type { ListingQuery } from "@/domain/schemas";
import { FilterFields } from "@/components/filter-fields";
import { Button } from "@/components/ui/button";

export function MobileFilterDrawer({ query }: { query: ListingQuery }) {
  return <Drawer.Root swipeDirection="right"><Drawer.Trigger className="inline-flex h-10 items-center gap-2 border border-border bg-white px-4 text-sm font-semibold lg:hidden"><SlidersHorizontal className="size-4" />Filters</Drawer.Trigger><Drawer.Portal><Drawer.Backdrop className="fixed inset-0 z-50 bg-black/55 transition-opacity duration-200 data-ending-style:opacity-0 data-starting-style:opacity-0" /><Drawer.Viewport className="fixed inset-0 z-50 flex justify-end"><Drawer.Popup className="h-full w-[min(92vw,400px)] overflow-y-auto bg-marble p-5 outline-none transition-transform duration-200 data-ending-style:translate-x-full data-starting-style:translate-x-full"><Drawer.Content><div className="mb-6 flex items-center justify-between"><Drawer.Title className="font-display text-3xl font-semibold uppercase">Filters</Drawer.Title><Drawer.Close aria-label="Close filters" className="inline-flex size-10 items-center justify-center"><X className="size-5" /></Drawer.Close></div><Drawer.Description className="sr-only">Filter UAE vehicle inventory</Drawer.Description><form action="/en-ae/cars"><FilterFields query={query} /><Button type="submit" variant="signal" className="mt-6 w-full">Show results</Button></form></Drawer.Content></Drawer.Popup></Drawer.Viewport></Drawer.Portal></Drawer.Root>;
}
