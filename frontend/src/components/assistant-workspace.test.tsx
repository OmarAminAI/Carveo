import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const profile = vi.hoisted(() => ({
  saveAssistantConversation: vi.fn().mockResolvedValue(undefined),
  archiveAssistantConversation: vi.fn(),
}));

vi.mock("@/profile/profile-provider", () => ({ useProfile: () => profile }));
import { AssistantWorkspace } from "@/components/assistant-workspace";

describe("AssistantWorkspace", () => {
  beforeEach(() => {
    profile.saveAssistantConversation.mockClear();
    profile.archiveAssistantConversation.mockClear();
  });

  it("keeps interpreted requirements editable and routes them to catalogue state", async () => {
    const user = userEvent.setup();
    render(<AssistantWorkspace initialPrompt="I need a GCC Toyota SUV under AED 180,000, 2021 or newer in Dubai" />);

    expect(screen.getByText("Fixture interpreter")).toBeInTheDocument();
    expect(screen.getByDisplayValue("180000")).toBeInTheDocument();
    await user.clear(screen.getByLabelText("Maximum budget"));
    await user.type(screen.getByLabelText("Maximum budget"), "200000");
    expect(screen.getByRole("link", { name: "Search now" })).toHaveAttribute("href", expect.stringContaining("priceMax=200000"));
  });

  it("persists deterministic buyer and assistant turns and retains history on start over", async () => {
    const user = userEvent.setup();
    render(<AssistantWorkspace />);

    await user.type(screen.getByLabelText("Add requirements"), "Toyota SUV under AED 180,000");
    await user.click(screen.getByRole("button", { name: "Send requirement" }));

    expect(profile.saveAssistantConversation).toHaveBeenCalledWith(expect.objectContaining({
      status: "active",
      turns: expect.arrayContaining([
        expect.objectContaining({ role: "buyer", content: "Toyota SUV under AED 180,000" }),
        expect.objectContaining({ role: "assistant" }),
      ]),
    }));
    await user.click(screen.getByRole("button", { name: "Start over" }));
    expect(profile.archiveAssistantConversation).toHaveBeenCalledTimes(1);
  });
});
