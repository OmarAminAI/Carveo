import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProfileProvider, useProfile } from "@/profile/profile-provider";
import { ShortlistButton } from "@/components/shortlist-button";
import { createEmptyProfile, PROFILE_STORAGE_KEY } from "@/profile/browser-profile";
import type { BuyerWorkspaceClient } from "@/profile/buyer-workspace-client";

const clerk = vi.hoisted(() => ({
  isLoaded: true,
  isSignedIn: false,
  userId: null as string | null,
  getToken: vi.fn().mockResolvedValue("token"),
}));

vi.mock("@clerk/nextjs", () => ({ useAuth: () => clerk }));

const workspace = {
  shortlistListingIds: ["server-listing"],
  comparisonListingIds: [],
  savedSearches: [],
  conversations: [],
  anonymousMergedAt: "2026-08-22T10:00:00Z",
};

function fakeClient(overrides: Partial<BuyerWorkspaceClient> = {}) {
  return {
    mergeAnonymous: vi.fn().mockResolvedValue({ workspace, merged: true, ignoredListingIds: [] }),
    getWorkspace: vi.fn().mockResolvedValue(workspace),
    addShortlist: vi.fn().mockResolvedValue(workspace),
    removeShortlist: vi.fn().mockResolvedValue(workspace),
    replaceComparison: vi.fn().mockResolvedValue(workspace),
    upsertSavedSearch: vi.fn(),
    createConversation: vi.fn(),
    appendTurn: vi.fn(),
    ...overrides,
  } as unknown as BuyerWorkspaceClient;
}

function ProfileProbe() {
  const { mode, profile, retrySync } = useProfile();
  return <div><span data-testid="mode">{mode}</span><span data-testid="shortlist">{profile.shortlistIds.join(",")}</span><button onClick={retrySync}>Retry sync</button></div>;
}

describe("ProfileProvider", () => {
  beforeEach(() => {
    localStorage.clear();
    clerk.isLoaded = true;
    clerk.isSignedIn = false;
    clerk.userId = null;
    clerk.getToken.mockClear();
  });

  it("persists shortlist state under the versioned browser profile", async () => {
    const user = userEvent.setup();
    render(<ProfileProvider><ShortlistButton listingId="listing-one" /></ProfileProvider>);

    await user.click(screen.getByRole("button", { name: "Add to shortlist" }));

    expect(screen.getByRole("button", { name: "Remove from shortlist" })).toBeInTheDocument();
    expect(JSON.parse(localStorage.getItem(PROFILE_STORAGE_KEY)!).shortlistIds).toEqual(["listing-one"]);
  });

  it("recovers from malformed browser storage", async () => {
    localStorage.setItem(PROFILE_STORAGE_KEY, "not-json");
    render(<ProfileProvider><ShortlistButton listingId="listing-one" /></ProfileProvider>);

    await waitFor(() => expect(() => JSON.parse(localStorage.getItem(PROFILE_STORAGE_KEY)!)).not.toThrow());
    expect(screen.getByRole("button", { name: "Add to shortlist" })).toBeInTheDocument();
  });

  it("merges anonymous state once and never writes account state to browser storage", async () => {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify({
      ...createEmptyProfile("browser"),
      shortlistIds: ["anonymous-listing"],
    }));
    clerk.isSignedIn = true;
    clerk.userId = "user_1";
    const client = fakeClient();

    render(<ProfileProvider workspaceClient={client}><ProfileProbe /></ProfileProvider>);

    await waitFor(() => expect(screen.getByTestId("mode")).toHaveTextContent("authenticated"));
    expect(screen.getByTestId("shortlist")).toHaveTextContent("server-listing");
    expect(client.mergeAnonymous).toHaveBeenCalledTimes(1);
    expect(client.mergeAnonymous).toHaveBeenCalledWith(expect.objectContaining({
      shortlistListingIds: ["anonymous-listing"],
    }));
    expect(localStorage.getItem(PROFILE_STORAGE_KEY)).toBeNull();
  });

  it("rolls back only the failed optimistic shortlist slice", async () => {
    clerk.isSignedIn = true;
    clerk.userId = "user_1";
    const client = fakeClient({ addShortlist: vi.fn().mockRejectedValue(new Error("offline")) });

    render(<ProfileProvider workspaceClient={client}><ShortlistButton listingId="new-listing" /><ProfileProbe /></ProfileProvider>);
    await waitFor(() => expect(screen.getByTestId("mode")).toHaveTextContent("authenticated"));

    await userEvent.click(screen.getByRole("button", { name: "Add to shortlist" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Add to shortlist" })).toBeInTheDocument());
    expect(screen.getByTestId("shortlist")).toHaveTextContent("server-listing");
    expect(screen.getByTestId("mode")).toHaveTextContent("error");
  });

  it("creates a fresh anonymous profile on sign-out without leaking account arrays", async () => {
    clerk.isSignedIn = true;
    clerk.userId = "user_1";
    const client = fakeClient();
    const view = render(<ProfileProvider workspaceClient={client}><ProfileProbe /></ProfileProvider>);
    await waitFor(() => expect(screen.getByTestId("mode")).toHaveTextContent("authenticated"));

    clerk.isSignedIn = false;
    clerk.userId = null;
    view.rerender(<ProfileProvider workspaceClient={client}><ProfileProbe /></ProfileProvider>);

    await waitFor(() => expect(screen.getByTestId("mode")).toHaveTextContent("anonymous"));
    expect(screen.getByTestId("shortlist")).toBeEmptyDOMElement();
    expect(JSON.parse(localStorage.getItem(PROFILE_STORAGE_KEY)!).shortlistIds).toEqual([]);
  });
});
