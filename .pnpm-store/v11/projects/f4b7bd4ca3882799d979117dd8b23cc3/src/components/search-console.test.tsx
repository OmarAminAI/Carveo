import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { SearchConsole } from "@/components/search-console";

describe("SearchConsole", () => {
  it("switches between direct and conversational search without hiding the primary action", async () => {
    const user = userEvent.setup();
    render(<SearchConsole />);

    expect(screen.getByRole("combobox", { name: "Make or model" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Describe what you need" }));
    expect(screen.getByRole("textbox", { name: "Describe your ideal car" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start AI search" })).toBeInTheDocument();
  });

  it("offers keyboard-ready make and model suggestions", async () => {
    const user = userEvent.setup();
    render(<SearchConsole />);

    await user.click(screen.getByRole("combobox", { name: "Make or model" }));
    await user.type(screen.getByRole("combobox", { name: "Make or model" }), "Land");

    expect(screen.getByText("Toyota Land Cruiser")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Search cars" })).toBeInTheDocument();
  });
});
