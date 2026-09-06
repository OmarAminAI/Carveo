"use client";

import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/profile/profile-provider";
import { cn } from "@/lib/utils";

export function ShortlistButton({ listingId, className }: { listingId: string; className?: string }) {
  const { profile, toggleShortlist } = useProfile();
  const selected = profile.shortlistIds.includes(listingId);
  return <Button type="button" size="icon" variant={selected ? "signal" : "outline"} className={cn(!selected && "bg-white", className)} aria-pressed={selected} aria-label={selected ? "Remove from shortlist" : "Add to shortlist"} onClick={() => toggleShortlist(listingId)}><Heart className={cn("size-4", selected && "fill-current")} /></Button>;
}
