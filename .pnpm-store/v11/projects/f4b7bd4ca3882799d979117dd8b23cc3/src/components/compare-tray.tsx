"use client";

import Link from "next/link";
import { ArrowRight, X } from "lucide-react";
import { useProfile } from "@/profile/profile-provider";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function CompareTray() {
  const { profile, removeComparison } = useProfile();
  if (!profile.compareIds.length) return null;
  const query = new URLSearchParams();
  profile.compareIds.forEach((id) => query.append("id", id));
  return <aside className="fixed inset-x-0 bottom-0 z-40 border-t border-white/20 bg-obsidian p-3 text-white"><div className="shell flex items-center justify-between gap-4"><div><p className="text-sm font-semibold">Compare set</p><p className="text-xs text-white/60">{profile.compareIds.length} of 4 cars selected</p></div><div className="hidden items-center gap-1 sm:flex">{profile.compareIds.map((id, index) => <button key={id} type="button" aria-label={`Remove car ${index + 1} from comparison`} onClick={() => removeComparison(id)} className="inline-flex h-8 items-center gap-2 border border-white/20 px-3 text-xs">Car {index + 1}<X className="size-3" /></button>)}</div><Link href={`/en-ae/compare?${query}`} className={cn(buttonVariants({ variant: "signal", size: "sm" }))}>Compare now <ArrowRight className="size-4" /></Link></div></aside>;
}
