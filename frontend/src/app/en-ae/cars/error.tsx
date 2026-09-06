"use client";

export default function CarsError({ reset }: { reset: () => void }) {
  return <main className="shell min-h-[60vh] py-20"><p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Car search</p><h1 className="font-display mt-3 text-4xl font-semibold uppercase">We couldn’t load these cars</h1><p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">Your search is still in the address bar. Try loading it again.</p><button onClick={reset} className="mt-6 min-h-11 bg-signal px-6 text-sm font-semibold">Try again</button></main>;
}
