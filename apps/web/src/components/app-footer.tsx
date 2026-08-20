import Link from "next/link";

export function AppFooter() {
  return (
    <footer className="border-t border-white/15 bg-obsidian py-12 text-white">
      <div className="shell grid gap-8 md:grid-cols-[1fr_auto_auto]">
        <div><p className="font-display text-3xl font-semibold uppercase">Carveo<span className="text-signal">.</span></p><p className="mt-3 max-w-sm text-sm text-white/60">Transparent UAE vehicle discovery using approved fixture data while source partnerships are reviewed.</p></div>
        <div className="grid gap-2 text-sm"><Link href="/en-ae/cars">Browse</Link><Link href="/en-ae/find">AI search</Link><Link href="/en-ae/compare">Compare</Link></div>
        <div className="text-sm text-white/60"><p>English · UAE</p><p className="mt-2">Prices in AED</p></div>
      </div>
    </footer>
  );
}
