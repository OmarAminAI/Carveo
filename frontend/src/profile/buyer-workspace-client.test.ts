import { describe, expect, it, vi } from "vitest";
import { createEmptyProfile } from "@/profile/browser-profile";
import {
  applyWorkspace,
  BuyerWorkspaceClient,
  toAnonymousMergePayload,
  WorkspaceRequestError,
} from "@/profile/buyer-workspace-client";

const emptyWorkspace = {
  shortlistListingIds: [],
  comparisonListingIds: [],
  savedSearches: [],
  conversations: [],
  anonymousMergedAt: null,
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("BuyerWorkspaceClient", () => {
  it("forwards the current bearer token without accepting a user identity", async () => {
    const getToken = vi.fn().mockResolvedValue("token-current");
    const fetcher = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(emptyWorkspace)));
    const client = new BuyerWorkspaceClient("http://localhost:8000", getToken, fetcher);

    await client.getWorkspace();

    expect(getToken).toHaveBeenCalledWith();
    const [url, init] = fetcher.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://localhost:8000/api/v1/me/workspace");
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer token-current");
    expect(JSON.stringify(init)).not.toContain("userId");
  });

  it("retries one 401 with a forced fresh token and does not retry again", async () => {
    const getToken = vi.fn()
      .mockResolvedValueOnce("token-stale")
      .mockResolvedValueOnce("token-fresh");
    const fetcher = vi.fn()
      .mockResolvedValueOnce(jsonResponse({ type: "unauthorized" }, 401))
      .mockResolvedValueOnce(jsonResponse(emptyWorkspace));
    const client = new BuyerWorkspaceClient("http://localhost:8000/", getToken, fetcher);

    await expect(client.getWorkspace()).resolves.toEqual(emptyWorkspace);
    expect(getToken).toHaveBeenNthCalledWith(1);
    expect(getToken).toHaveBeenNthCalledWith(2, { skipCache: true });
    expect(fetcher).toHaveBeenCalledTimes(2);
    expect(new Headers(fetcher.mock.calls[1]?.[1]?.headers).get("Authorization")).toBe("Bearer token-fresh");
  });

  it("throws a typed error for non-auth failures and malformed responses", async () => {
    const getToken = vi.fn().mockResolvedValue("token-current");
    const unavailable = new BuyerWorkspaceClient(
      "http://localhost:8000",
      getToken,
      vi.fn().mockResolvedValue(jsonResponse({ detail: "down" }, 503)),
    );
    const malformed = new BuyerWorkspaceClient(
      "http://localhost:8000",
      getToken,
      vi.fn().mockResolvedValue(jsonResponse({ shortlistListingIds: "wrong" })),
    );

    await expect(unavailable.getWorkspace()).rejects.toBeInstanceOf(WorkspaceRequestError);
    await expect(unavailable.getWorkspace()).rejects.toMatchObject({ status: 503 });
    await expect(malformed.getWorkspace()).rejects.toThrow();
  });

  it("sets content type only for JSON bodies", async () => {
    const fetcher = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(emptyWorkspace)));
    const client = new BuyerWorkspaceClient("http://localhost:8000", async () => "token", fetcher);

    await client.getWorkspace();
    await client.replaceComparison(["one", "two"]);

    expect(new Headers(fetcher.mock.calls[0]?.[1]?.headers).has("Content-Type")).toBe(false);
    expect(new Headers(fetcher.mock.calls[1]?.[1]?.headers).get("Content-Type")).toBe("application/json");
  });
});

describe("workspace profile conversion", () => {
  it("builds an anonymous merge without recent views or profile identity", () => {
    const profile = {
      ...createEmptyProfile("browser-profile"),
      shortlistIds: ["listing-one"],
      compareIds: ["listing-two"],
      recentViewIds: ["private-recent-view"],
      savedSearchDrafts: [{ id: "draft", label: "SUV", query: "bodyType=SUV", savedAt: "2026-08-22" }],
      anonymousConversations: [{
        clientId: "client-1",
        title: "Family SUV",
        status: "active" as const,
        interpretedIntent: { bodyType: ["SUV"] },
        createdAt: "2026-08-22T10:00:00Z",
        updatedAt: "2026-08-22T10:00:00Z",
        turns: [{ id: "turn-1", role: "buyer" as const, content: "Seven seats" }],
      }],
    };

    const payload = toAnonymousMergePayload(profile);

    expect(payload).toEqual({
      shortlistListingIds: ["listing-one"],
      comparisonListingIds: ["listing-two"],
      savedSearches: [{ label: "SUV", query: "bodyType=SUV" }],
      conversations: [{
        clientId: "client-1",
        title: "Family SUV",
        interpretedIntent: { bodyType: ["SUV"] },
        turns: [{ role: "buyer", content: "Seven seats" }],
      }],
    });
    expect(JSON.stringify(payload)).not.toContain("private-recent-view");
    expect(JSON.stringify(payload)).not.toContain("browser-profile");
  });

  it("applies authoritative account arrays while preserving local recent views", () => {
    const profile = { ...createEmptyProfile("browser"), recentViewIds: ["recent"] };
    const next = applyWorkspace(profile, {
      ...emptyWorkspace,
      shortlistListingIds: ["server-shortlist"],
      comparisonListingIds: ["server-compare"],
      savedSearches: [{
        id: "11111111-1111-4111-8111-111111111111",
        label: "Server search",
        query: "make=Toyota",
        createdAt: "2026-08-22T10:00:00Z",
        updatedAt: "2026-08-22T11:00:00Z",
      }],
    });

    expect(next.shortlistIds).toEqual(["server-shortlist"]);
    expect(next.compareIds).toEqual(["server-compare"]);
    expect(next.savedSearchDrafts[0]).toMatchObject({ label: "Server search", query: "make=Toyota" });
    expect(next.recentViewIds).toEqual(["recent"]);
    expect(next.anonymousConversations).toEqual([]);
  });
});
