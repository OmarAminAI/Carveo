import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { MarketCharts } from "@/components/market-charts";
import { fixtureCatalogue } from "@/data/fixture-catalogue";

describe("MarketCharts", () => {
  it("filters the segment by trim and regional specification", async () => {
    const user = userEvent.setup();
    const listings = fixtureCatalogue.filter((listing) => listing.model === "Land Cruiser");
    render(<MarketCharts listings={listings} />);

    await user.selectOptions(screen.getByLabelText("Trim"), "VXR");
    await user.selectOptions(screen.getByLabelText("Specifications"), "GCC");

    expect(screen.getByText("1 matching fixture")).toBeInTheDocument();
  });
});
