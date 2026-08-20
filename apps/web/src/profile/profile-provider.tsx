"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { BrowserProfile } from "@/domain/schemas";
import {
  addComparison,
  createEmptyProfile,
  migrateProfile,
  PROFILE_STORAGE_KEY,
  recordRecentView,
  removeComparison,
  saveSearchDraft,
  toggleShortlist,
} from "@/profile/browser-profile";

type ProfileContextValue = {
  profile: BrowserProfile;
  hydrated: boolean;
  toggleShortlist: (listingId: string) => void;
  toggleComparison: (listingId: string) => void;
  removeComparison: (listingId: string) => void;
  saveSearchDraft: (draft: { label: string; query: string }) => void;
  recordRecentView: (listingId: string) => void;
};

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfile] = useState(() => createEmptyProfile("pending"));
  const [hydrated, setHydrated] = useState(false);
  useEffect(() => {
    const stored = localStorage.getItem(PROFILE_STORAGE_KEY);
    const id = crypto.randomUUID();
    let parsed: unknown = null;
    try { parsed = stored ? JSON.parse(stored) : null; } catch { parsed = null; }
    setProfile(parsed ? migrateProfile(parsed, id) : createEmptyProfile(id));
    setHydrated(true);
  }, []);
  useEffect(() => { if (hydrated) localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile)); }, [profile, hydrated]);
  const toggleShortlistAction = useCallback((listingId: string) => setProfile((current) => toggleShortlist(current, listingId)), []);
  const toggleComparisonAction = useCallback((listingId: string) => setProfile((current) => current.compareIds.includes(listingId) ? removeComparison(current, listingId) : addComparison(current, listingId)), []);
  const removeComparisonAction = useCallback((listingId: string) => setProfile((current) => removeComparison(current, listingId)), []);
  const saveSearchDraftAction = useCallback((draft: { label: string; query: string }) => setProfile((current) => saveSearchDraft(current, draft)), []);
  const recordRecentViewAction = useCallback((listingId: string) => setProfile((current) => recordRecentView(current, listingId)), []);
  const value = useMemo<ProfileContextValue>(() => ({
    profile,
    hydrated,
    toggleShortlist: toggleShortlistAction,
    toggleComparison: toggleComparisonAction,
    removeComparison: removeComparisonAction,
    saveSearchDraft: saveSearchDraftAction,
    recordRecentView: recordRecentViewAction,
  }), [profile, hydrated, recordRecentViewAction, removeComparisonAction, saveSearchDraftAction, toggleComparisonAction, toggleShortlistAction]);
  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const context = useContext(ProfileContext);
  if (!context) throw new Error("useProfile must be used within ProfileProvider");
  return context;
}
