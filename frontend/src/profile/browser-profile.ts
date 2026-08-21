import { anonymousConversationSchema, type BrowserProfile } from "@/domain/schemas";

export const PROFILE_STORAGE_KEY = "carveo.profile.v1";

export function createEmptyProfile(id = crypto.randomUUID()): BrowserProfile {
  return {
    version: 2,
    id,
    shortlistIds: [],
    compareIds: [],
    recentViewIds: [],
    savedSearchDrafts: [],
    assistantDraft: "",
    anonymousConversations: [],
  };
}

const stringArray = (value: unknown) => Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];

export function migrateProfile(value: unknown, fallbackId = crypto.randomUUID()): BrowserProfile {
  if (!value || typeof value !== "object") return createEmptyProfile(fallbackId);
  const source = value as Record<string, unknown>;
  const anonymousConversations = Array.isArray(source.anonymousConversations)
    ? source.anonymousConversations.flatMap((item) => {
        const parsed = anonymousConversationSchema.safeParse(item);
        return parsed.success ? [parsed.data] : [];
      })
    : [];
  return {
    version: 2,
    id: typeof source.id === "string" ? source.id : fallbackId,
    shortlistIds: stringArray(source.shortlistIds),
    compareIds: stringArray(source.compareIds).slice(0, 4),
    recentViewIds: stringArray(source.recentViewIds).slice(0, 12),
    savedSearchDrafts: Array.isArray(source.savedSearchDrafts) ? source.savedSearchDrafts.filter((item): item is BrowserProfile["savedSearchDrafts"][number] => Boolean(item && typeof item === "object" && "query" in item)) : [],
    assistantDraft: typeof source.assistantDraft === "string" ? source.assistantDraft : "",
    anonymousConversations,
  };
}

export function addComparison(profile: BrowserProfile, listingId: string): BrowserProfile {
  if (profile.compareIds.includes(listingId) || profile.compareIds.length >= 4) return profile;
  return { ...profile, compareIds: [...profile.compareIds, listingId] };
}

export function removeComparison(profile: BrowserProfile, listingId: string): BrowserProfile { return { ...profile, compareIds: profile.compareIds.filter((id) => id !== listingId) }; }

export function toggleShortlist(profile: BrowserProfile, listingId: string): BrowserProfile {
  return { ...profile, shortlistIds: profile.shortlistIds.includes(listingId) ? profile.shortlistIds.filter((id) => id !== listingId) : [...profile.shortlistIds, listingId] };
}

export function saveSearchDraft(
  profile: BrowserProfile,
  draft: { label: string; query: string },
  savedAt = new Date().toISOString(),
): BrowserProfile {
  const existing = profile.savedSearchDrafts.find((item) => item.query === draft.query);
  const next = {
    id: existing?.id ?? crypto.randomUUID(),
    label: draft.label,
    query: draft.query,
    savedAt,
  };
  return {
    ...profile,
    savedSearchDrafts: [next, ...profile.savedSearchDrafts.filter((item) => item.query !== draft.query)].slice(0, 12),
  };
}

export function recordRecentView(profile: BrowserProfile, listingId: string): BrowserProfile {
  if (profile.recentViewIds[0] === listingId) return profile;
  return {
    ...profile,
    recentViewIds: [listingId, ...profile.recentViewIds.filter((id) => id !== listingId)].slice(0, 12),
  };
}
