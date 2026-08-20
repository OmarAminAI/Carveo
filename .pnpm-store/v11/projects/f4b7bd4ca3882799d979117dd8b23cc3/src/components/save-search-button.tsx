"use client";

import { useState } from "react";
import { BookmarkCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useProfile } from "@/profile/profile-provider";

export function SaveSearchButton({ query, label }: { query: string; label: string }) {
  const { saveSearchDraft } = useProfile();
  const [saved, setSaved] = useState(false);
  return <Button type="button" variant="outline" onClick={() => { saveSearchDraft({ query, label }); setSaved(true); }}><BookmarkCheck className="size-4" />{saved ? "Saved locally" : "Save search"}</Button>;
}
