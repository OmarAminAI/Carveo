"use client";

import { useAuth } from "@clerk/nextjs";
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { AnonymousConversation, BrowserProfile, BuyerWorkspace } from "@/domain/schemas";
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
import {
  applyWorkspace,
  BuyerWorkspaceClient,
  toAnonymousMergePayload,
} from "@/profile/buyer-workspace-client";

export type ProfileMode = "loading" | "anonymous" | "authenticated" | "error";

type ProfileContextValue = {
  profile: BrowserProfile;
  hydrated: boolean;
  mode: ProfileMode;
  errorMessage: string | null;
  retrySync: () => void;
  toggleShortlist: (listingId: string) => void;
  toggleComparison: (listingId: string) => void;
  removeComparison: (listingId: string) => void;
  saveSearchDraft: (draft: { label: string; query: string }) => void;
  recordRecentView: (listingId: string) => void;
  saveAssistantConversation: (conversation: AnonymousConversation) => Promise<void>;
  archiveAssistantConversation: (clientId: string) => void;
};

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function ProfileProvider({
  children,
  workspaceClient,
}: {
  children: React.ReactNode;
  workspaceClient?: BuyerWorkspaceClient;
}) {
  const { isLoaded, isSignedIn, userId, getToken } = useAuth();
  const [profile, setProfileState] = useState(() => createEmptyProfile("pending"));
  const [hydrated, setHydrated] = useState(false);
  const [mode, setMode] = useState<ProfileMode>("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [syncVersion, setSyncVersion] = useState(0);
  const profileRef = useRef(profile);
  const confirmedRef = useRef(profile);
  const lastUserRef = useRef<string | null>(null);
  const generationRef = useRef(0);
  const lastSyncKeyRef = useRef<string | null>(null);
  const conversationIdsRef = useRef(new Map<string, string>());
  const conversationTurnCountsRef = useRef(new Map<string, number>());

  const client = useMemo(
    () => workspaceClient ?? new BuyerWorkspaceClient(
      process.env.NEXT_PUBLIC_CARVEO_API_URL ?? "http://localhost:8000",
      (options) => getToken(options),
    ),
    [getToken, workspaceClient],
  );

  const setProfile = useCallback((next: BrowserProfile | ((current: BrowserProfile) => BrowserProfile)) => {
    setProfileState((current) => {
      const resolved = typeof next === "function" ? next(current) : next;
      profileRef.current = resolved;
      return resolved;
    });
  }, []);

  const acceptWorkspace = useCallback((workspace: BuyerWorkspace) => {
    const next = applyWorkspace(profileRef.current, workspace);
    confirmedRef.current = next;
    setProfile(next);
  }, [setProfile]);

  useEffect(() => {
    const stored = localStorage.getItem(PROFILE_STORAGE_KEY);
    const id = crypto.randomUUID();
    let parsed: unknown = null;
    try { parsed = stored ? JSON.parse(stored) : null; } catch { parsed = null; }
    const next = parsed ? migrateProfile(parsed, id) : createEmptyProfile(id);
    profileRef.current = next;
    confirmedRef.current = next;
    setProfileState(next);
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated && mode === "anonymous") {
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
    }
  }, [hydrated, mode, profile]);

  useEffect(() => {
    if (!hydrated || !isLoaded) return;
    const generation = ++generationRef.current;

    if (!isSignedIn || !userId) {
      if (lastUserRef.current !== null) {
        const fresh = createEmptyProfile();
        fresh.recentViewIds = profileRef.current.recentViewIds;
        profileRef.current = fresh;
        confirmedRef.current = fresh;
        setProfileState(fresh);
        localStorage.removeItem(PROFILE_STORAGE_KEY);
      }
      lastUserRef.current = null;
      lastSyncKeyRef.current = null;
      conversationIdsRef.current.clear();
      conversationTurnCountsRef.current.clear();
      setErrorMessage(null);
      setMode("anonymous");
      return;
    }

    const syncKey = `${userId}:${syncVersion}`;
    if (lastSyncKeyRef.current === syncKey) return;
    lastSyncKeyRef.current = syncKey;
    lastUserRef.current = userId;
    setMode("loading");
    setErrorMessage(null);
    const anonymousProfile = profileRef.current;

    void client.mergeAnonymous(toAnonymousMergePayload(anonymousProfile)).then((response) => {
      if (generationRef.current !== generation) return;
      localStorage.removeItem(PROFILE_STORAGE_KEY);
      acceptWorkspace(response.workspace);
      setMode("authenticated");
    }).catch(() => {
      if (generationRef.current !== generation) return;
      setMode("error");
      setErrorMessage("Your buyer workspace could not be synchronized.");
    });
  }, [acceptWorkspace, client, hydrated, isLoaded, isSignedIn, mode, syncVersion, userId]);

  const failMutation = useCallback((slice: "shortlist" | "comparison" | "saved-searches") => {
    setProfile((current) => {
      const confirmed = confirmedRef.current;
      if (slice === "shortlist") return { ...current, shortlistIds: confirmed.shortlistIds };
      if (slice === "comparison") return { ...current, compareIds: confirmed.compareIds };
      return { ...current, savedSearchDrafts: confirmed.savedSearchDrafts };
    });
    setMode("error");
    setErrorMessage("That change could not be synchronized. Your last confirmed state was restored.");
  }, [setProfile]);

  const toggleShortlistAction = useCallback((listingId: string) => {
    const removing = profileRef.current.shortlistIds.includes(listingId);
    setProfile((current) => toggleShortlist(current, listingId));
    if (!isSignedIn) return;
    const request = removing ? client.removeShortlist(listingId) : client.addShortlist(listingId);
    void request.then(acceptWorkspace).catch(() => failMutation("shortlist"));
  }, [acceptWorkspace, client, failMutation, isSignedIn, setProfile]);

  const toggleComparisonAction = useCallback((listingId: string) => {
    const current = profileRef.current;
    const next = current.compareIds.includes(listingId)
      ? removeComparison(current, listingId)
      : addComparison(current, listingId);
    setProfile(next);
    if (!isSignedIn || next === current) return;
    void client.replaceComparison(next.compareIds).then(acceptWorkspace).catch(() => failMutation("comparison"));
  }, [acceptWorkspace, client, failMutation, isSignedIn, setProfile]);

  const removeComparisonAction = useCallback((listingId: string) => {
    const next = removeComparison(profileRef.current, listingId);
    setProfile(next);
    if (!isSignedIn) return;
    void client.replaceComparison(next.compareIds).then(acceptWorkspace).catch(() => failMutation("comparison"));
  }, [acceptWorkspace, client, failMutation, isSignedIn, setProfile]);

  const saveSearchDraftAction = useCallback((draft: { label: string; query: string }) => {
    setProfile((current) => saveSearchDraft(current, draft));
    if (!isSignedIn) return;
    void client.upsertSavedSearch(draft).then((saved) => {
      const next = saveSearchDraft(profileRef.current, draft, saved.updatedAt);
      next.savedSearchDrafts = next.savedSearchDrafts.map((item) => item.query === saved.query
        ? { id: saved.id, label: saved.label, query: saved.query, savedAt: saved.updatedAt }
        : item);
      confirmedRef.current = { ...confirmedRef.current, savedSearchDrafts: next.savedSearchDrafts };
      setProfile(next);
    }).catch(() => failMutation("saved-searches"));
  }, [client, failMutation, isSignedIn, setProfile]);

  const recordRecentViewAction = useCallback((listingId: string) => {
    setProfile((current) => recordRecentView(current, listingId));
  }, [setProfile]);

  const saveAssistantConversation = useCallback(async (conversation: AnonymousConversation) => {
    if (!isSignedIn) {
      setProfile((current) => ({
        ...current,
        anonymousConversations: [
          conversation,
          ...current.anonymousConversations.filter((item) => item.clientId !== conversation.clientId),
        ],
      }));
      return;
    }

    try {
      let conversationId = conversationIdsRef.current.get(conversation.clientId);
      let syncedTurns = conversationTurnCountsRef.current.get(conversation.clientId) ?? 0;
      if (!conversationId) {
        const created = await client.createConversation({
          clientId: conversation.clientId,
          title: conversation.title,
          interpretedIntent: conversation.interpretedIntent,
          turns: conversation.turns.map(({ role, content }) => ({ role, content })),
        });
        conversationId = created.id;
        syncedTurns = created.turns.length;
        conversationIdsRef.current.set(conversation.clientId, conversationId);
      }
      for (const turn of conversation.turns.slice(syncedTurns)) {
        const updated = await client.appendTurn(conversationId, { role: turn.role, content: turn.content });
        syncedTurns = updated.turns.length;
      }
      conversationTurnCountsRef.current.set(conversation.clientId, syncedTurns);
    } catch {
      setMode("error");
      setErrorMessage("This conversation could not be synchronized.");
    }
  }, [client, isSignedIn, setProfile]);

  const archiveAssistantConversation = useCallback((clientId: string) => {
    if (isSignedIn) return;
    setProfile((current) => ({
      ...current,
      anonymousConversations: current.anonymousConversations.map((conversation) => conversation.clientId === clientId
        ? { ...conversation, status: "archived" }
        : conversation),
    }));
  }, [isSignedIn, setProfile]);

  const retrySync = useCallback(() => setSyncVersion((value) => value + 1), []);
  const value = useMemo<ProfileContextValue>(() => ({
    profile,
    hydrated,
    mode,
    errorMessage,
    retrySync,
    toggleShortlist: toggleShortlistAction,
    toggleComparison: toggleComparisonAction,
    removeComparison: removeComparisonAction,
    saveSearchDraft: saveSearchDraftAction,
    recordRecentView: recordRecentViewAction,
    saveAssistantConversation,
    archiveAssistantConversation,
  }), [
    archiveAssistantConversation,
    errorMessage,
    hydrated,
    mode,
    profile,
    recordRecentViewAction,
    removeComparisonAction,
    retrySync,
    saveAssistantConversation,
    saveSearchDraftAction,
    toggleComparisonAction,
    toggleShortlistAction,
  ]);

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const context = useContext(ProfileContext);
  if (!context) throw new Error("useProfile must be used within ProfileProvider");
  return context;
}
