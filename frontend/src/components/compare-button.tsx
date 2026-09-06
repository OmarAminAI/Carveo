"use client";

import { Columns3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/profile/profile-provider";

export function CompareButton({ listingId }: { listingId: string }) {
  const { profile, toggleComparison } = useProfile();
  const selected = profile.compareIds.includes(listingId);
  const disabled = !selected && profile.compareIds.length >= 4;
  return <Button type="button" variant={selected ? "signal" : "outline"} size="sm" className={selected ? "min-h-10" : "min-h-10 bg-white"} aria-pressed={selected} disabled={disabled} title={disabled ? "You can compare up to four cars. Remove one to add another." : undefined} onClick={() => toggleComparison(listingId)}><Columns3 className="size-4" />{selected ? "Added" : "Compare"}</Button>;
}
