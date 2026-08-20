import Link from "next/link";
import { Heart, Sparkles } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { MobileNavigation } from "@/components/mobile-navigation";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/15 bg-obsidian text-white">
      <div className="shell flex h-16 items-center justify-between gap-6">
        <Link href="/en-ae" className="font-display text-3xl font-semibold uppercase">Carveo<span className="text-signal">.</span></Link>
        <nav className="hidden items-center gap-7 text-sm md:flex" aria-label="Primary navigation">
          <Link href="/en-ae/cars" className="hover:text-signal">Browse cars</Link>
          <Link href="/en-ae/market/toyota/land-cruiser" className="hover:text-signal">Market insights</Link>
          <Link href="/en-ae/find" className="inline-flex items-center gap-2 hover:text-signal"><Sparkles className="size-4" />AI search</Link>
        </nav>
        <div className="flex items-center gap-1">
          <Link href="/en-ae/shortlist" aria-label="Shortlist" className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "text-white")}><Heart className="size-5" /></Link>
          <MobileNavigation />
        </div>
      </div>
    </header>
  );
}
