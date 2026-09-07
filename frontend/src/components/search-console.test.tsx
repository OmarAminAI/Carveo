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

  it("keeps the search mode labels on one line", () => {
    render(<SearchConsole />);

    expect(screen.getByRole("button", { name: "Search inventory" })).toHaveClass("whitespace-nowrap");
    expect(screen.getByRole("button", { name: "Describe what you need" })).toHaveClass("whitespace-nowrap");
  });

  it("keeps the mode toggle stacked until the panel is wide enough for both labels", () => {
    render(<SearchConsole />);

    expect(screen.getByRole("group", { name: "Search mode" })).toHaveClass("md:flex");
    expect(screen.getByRole("group", { name: "Search mode" })).not.toHaveClass("sm:grid-cols-2");
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
