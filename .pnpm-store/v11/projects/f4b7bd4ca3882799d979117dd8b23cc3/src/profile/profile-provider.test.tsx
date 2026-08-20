import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { ProfileProvider } from "@/profile/profile-provider";
import { ShortlistButton } from "@/components/shortlist-button";
import { PROFILE_STORAGE_KEY } from "@/profile/browser-profile";

describe("ProfileProvider", () => {
  beforeEach(() => localStorage.clear());

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
});
