"use client";

import { useEffect } from "react";
import { useProfile } from "@/profile/profile-provider";

export function RecentViewRecorder({ listingId }: { listingId: string }) {
  const { recordRecentView } = useProfile();
  useEffect(() => { recordRecentView(listingId); }, [listingId, recordRecentView]);
  return null;
}
