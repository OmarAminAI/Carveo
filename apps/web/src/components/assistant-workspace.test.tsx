import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AssistantWorkspace } from "@/components/assistant-workspace";

describe("AssistantWorkspace", () => {
  it("keeps interpreted requirements editable and routes them to catalogue state", async () => {
    const user = userEvent.setup();
    render(<AssistantWorkspace initialPrompt="I need a GCC Toyota SUV under AED 180,000, 2021 or newer in Dubai" />);

    expect(screen.getByText("Fixture interpreter")).toBeInTheDocument();
    expect(screen.getByDisplayValue("180000")).toBeInTheDocument();
    await user.clear(screen.getByLabelText("Maximum budget"));
    await user.type(screen.getByLabelText("Maximum budget"), "200000");
    expect(screen.getByRole("link", { name: "Search now" })).toHaveAttribute("href", expect.stringContaining("priceMax=200000"));
  });
});
