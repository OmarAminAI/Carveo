"use client";

import { Button } from "@/components/ui/button";

export default function LocaleError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main className="min-h-[70vh] bg-marble"><div className="shell py-20"><p className="text-xs font-semibold uppercase text-muted-foreground">Recoverable error</p><h1 className="font-display mt-2 text-5xl font-semibold uppercase">The catalogue could not load</h1><p className="mt-3 max-w-xl text-sm text-muted-foreground">Your browser workspace is still local. Retry this view without clearing your shortlist or comparison.</p><Button className="mt-6" onClick={reset}>Try again</Button></div></main>;
}
