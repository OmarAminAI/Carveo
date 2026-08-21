"use client";

import { useState } from "react";
import { BookmarkCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/profile/profile-provider";

export function SaveSearchButton({ query, label }: { query: string; label: string }) {
  const { mode, saveSearchDraft } = useProfile();
  const [saved, setSaved] = useState(false);
  const savedLabel = mode === "authenticated" ? "Saved to profile" : "Saved locally";
  return <Button type="button" variant="outline" onClick={() => { saveSearchDraft({ query, label }); setSaved(true); }}><BookmarkCheck className="size-4" />{saved ? savedLabel : "Save search"}</Button>;
}
