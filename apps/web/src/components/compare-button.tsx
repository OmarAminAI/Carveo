"use client";

import { Columns3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/profile/profile-provider";

export function CompareButton({ listingId }: { listingId: string }) {
  const { profile, toggleComparison } = useProfile();
  const selected = profile.compareIds.includes(listingId);
  const disabled = !selected && profile.compareIds.length >= 4;
  return <Button type="button" variant={selected ? "signal" : "outline"} size="sm" disabled={disabled} onClick={() => toggleComparison(listingId)}><Columns3 className="size-4" />{selected ? "Added" : "Compare"}</Button>;
}
