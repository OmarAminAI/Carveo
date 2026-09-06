import { describe, expect, it } from "vitest";
import { buildComparisonRows } from "@/components/comparison-workspace";
import { fixtureCatalogue } from "@/data/fixture-catalogue";

describe("comparison row model", () => {
  it("leads with the four buying decisions", () => {
    expect(buildComparisonRows(fixtureCatalogue.slice(0, 2)).slice(0, 4).map((row) => row.label))
      .toEqual(["Price", "Mileage", "Year", "Condition"]);
  });

  it("surfaces warnings before positive claims and keeps absent evidence unknown", () => {
    const listing = fixtureCatalogue[0];
    const rows = buildComparisonRows([
      { ...listing, conditionEvidence: [
        { kind: "positive", label: "Service history stated", detail: "Records available" },
        { kind: "warning", label: "Repair stated", detail: "Bumper repaired" },
      ] },
      { ...listing, conditionEvidence: [] },
    ]);
    expect(rows.find((row) => row.label === "Condition")?.values).toEqual(["Repair stated", "Condition not stated"]);
  });
  it("marks only rows whose selected values differ", () => {
    const listings = [fixtureCatalogue[0], fixtureCatalogue[1]];
    const rows = buildComparisonRows(listings);

    expect(rows.find((row) => row.label === "Make")?.different).toBe(false);
    expect(rows.find((row) => row.label === "Price")?.different).toBe(true);
    expect(rows.find((row) => row.label === "Seller")?.different).toBe(true);
  });
});
