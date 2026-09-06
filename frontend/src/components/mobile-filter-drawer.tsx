"use client";

import { useState } from "react";
import { Drawer } from "@base-ui/react/drawer";
import { SlidersHorizontal, X } from "lucide-react";
import type { ListingQuery } from "@/domain/schemas";
import { FilterForm } from "@/components/browse-navigation";

export function MobileFilterDrawer({ query, currentParams }: { query: ListingQuery; currentParams: string }) {
  const [open, setOpen] = useState(false);
  return <Drawer.Root open={open} onOpenChange={setOpen} swipeDirection="right">
    <Drawer.Trigger className="inline-flex h-11 items-center gap-2 rounded-lg border border-border bg-white px-4 text-sm font-semibold lg:hidden"><SlidersHorizontal className="size-4" />Filters</Drawer.Trigger>
    <Drawer.Portal><Drawer.Backdrop className="fixed inset-0 z-50 bg-black/55 transition-opacity duration-200 data-ending-style:opacity-0 data-starting-style:opacity-0 motion-reduce:transition-none" /><Drawer.Viewport className="fixed inset-0 z-50 flex justify-end"><Drawer.Popup className="h-full w-[min(92vw,400px)] overflow-y-auto bg-white p-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] outline-none transition-transform duration-200 data-ending-style:translate-x-full data-starting-style:translate-x-full motion-reduce:transition-none"><Drawer.Content>
      <div className="mb-2 flex items-center justify-between"><Drawer.Title className="font-display text-3xl font-semibold uppercase">Find your fit</Drawer.Title><Drawer.Close aria-label="Close filters" className="inline-flex size-11 items-center justify-center rounded-lg hover:bg-marble"><X className="size-5" /></Drawer.Close></div>
      <Drawer.Description className="mb-6 text-sm text-muted-foreground">Choose what matters. Apply when you’re ready.</Drawer.Description>
      {open && <FilterForm key={currentParams} query={query} currentParams={currentParams} mobile onApplied={() => setOpen(false)} />}
    </Drawer.Content></Drawer.Popup></Drawer.Viewport></Drawer.Portal>
  </Drawer.Root>;
}
