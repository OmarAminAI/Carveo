import { describe, expect, it } from "vitest";
import { buildComparisonRows } from "@/components/comparison-workspace";
import { fixtureCatalogue } from "@/data/fixture-catalogue";

describe("comparison row model", () => {
  it("marks only rows whose selected values differ", () => {
    const listings = [fixtureCatalogue[0], fixtureCatalogue[1]];
    const rows = buildComparisonRows(listings);

    expect(rows.find((row) => row.label === "Make")?.different).toBe(false);
    expect(rows.find((row) => row.label === "Price")?.different).toBe(true);
    expect(rows.find((row) => row.label === "Seller")?.different).toBe(true);
  });
});
