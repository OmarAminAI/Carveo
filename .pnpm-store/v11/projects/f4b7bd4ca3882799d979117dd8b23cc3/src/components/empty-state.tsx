import Link from "next/link";
import { SearchX } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";

export function EmptyState() { return <div className="flex min-h-96 flex-col items-center justify-center border border-dashed border-border bg-white p-8 text-center"><SearchX className="size-8 text-steel" /><h2 className="font-display mt-5 text-3xl font-semibold uppercase">No matching cars</h2><p className="mt-2 max-w-md text-sm text-muted-foreground">Try widening the budget, year, or specification filters. Unknown condition evidence remains included unless you explicitly filter it out.</p><Link href="/en-ae/cars" className={`${buttonVariants({ variant: "default" })} mt-6`}>Clear all filters</Link></div>; }
