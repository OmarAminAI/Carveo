import { describe, expect, it } from "vitest";
import {
  addComparison,
  createEmptyProfile,
  migrateProfile,
  recordRecentView,
  saveSearchDraft,
  toggleShortlist,
} from "@/profile/browser-profile";

describe("browser profile", () => {
  it("keeps comparison selection unique and capped at four", () => {
    let profile = createEmptyProfile("profile-test");
    for (const id of ["one", "two", "three", "four", "five", "two"]) {
      profile = addComparison(profile, id);
    }

    expect(profile.compareIds).toEqual(["one", "two", "three", "four"]);
  });

  it("toggles shortlist entries without duplicates", () => {
    const initial = createEmptyProfile("profile-test");
    const added = toggleShortlist(initial, "listing-one");
    const removed = toggleShortlist(added, "listing-one");

    expect(added.shortlistIds).toEqual(["listing-one"]);
    expect(removed.shortlistIds).toEqual([]);
  });

  it("migrates version-one and malformed storage into a usable v2 profile", () => {
    expect(migrateProfile({ version: 0, shortlistIds: ["old"] }, "fallback")).toEqual(
      expect.objectContaining({
        version: 2,
        id: "fallback",
        shortlistIds: ["old"],
        compareIds: [],
        anonymousConversations: [],
      }),
    );
    expect(migrateProfile("broken", "fallback")).toEqual(createEmptyProfile("fallback"));
  });

  it("keeps only valid anonymous conversations during profile migration", () => {
    const migrated = migrateProfile({
      version: 2,
      anonymousConversations: [
        {
          clientId: "conversation-1",
          title: "Family SUV",
          status: "active",
          interpretedIntent: {},
          createdAt: "2026-08-22T10:00:00Z",
          updatedAt: "2026-08-22T10:00:00Z",
          turns: [{ id: "turn-1", role: "buyer", content: "Seven seats" }],
        },
        { clientId: 42 },
      ],
    }, "fallback");

    expect(migrated.anonymousConversations).toHaveLength(1);
    expect(migrated.anonymousConversations[0]?.clientId).toBe("conversation-1");
  });

  it("saves a search once and moves a repeated query to the front", () => {
    const initial = createEmptyProfile("profile-test");
    const first = saveSearchDraft(initial, { label: "Family SUVs", query: "bodyType=SUV&priceMax=180000" }, "2026-08-20T10:00:00Z");
    const second = saveSearchDraft(first, { label: "Updated SUV search", query: "bodyType=SUV&priceMax=180000" }, "2026-08-20T11:00:00Z");

    expect(second.savedSearchDrafts).toHaveLength(1);
    expect(second.savedSearchDrafts[0]).toMatchObject({ label: "Updated SUV search", savedAt: "2026-08-20T11:00:00Z" });
  });

  it("records unique recent views in recency order and caps the list", () => {
    let profile = createEmptyProfile("profile-test");
    for (let index = 0; index < 14; index += 1) profile = recordRecentView(profile, `listing-${index}`);
    profile = recordRecentView(profile, "listing-5");

    expect(profile.recentViewIds).toHaveLength(12);
    expect(profile.recentViewIds[0]).toBe("listing-5");
    expect(profile.recentViewIds.filter((id) => id === "listing-5")).toHaveLength(1);
  });
});
