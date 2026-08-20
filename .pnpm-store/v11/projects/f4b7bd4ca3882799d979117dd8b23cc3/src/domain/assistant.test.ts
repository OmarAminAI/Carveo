import { describe, expect, it } from "vitest";
import { interpretFixturePrompt } from "@/domain/assistant";

describe("fixture assistant", () => {
  it("extracts a deterministic intent without implying a remote AI call", () => {
    const result = interpretFixturePrompt(
      "I need a GCC Toyota SUV under AED 180,000, 2021 or newer in Dubai",
    );

    expect(result.mode).toBe("fixture");
    expect(result.intent).toEqual(
      expect.objectContaining({
        make: ["Toyota"],
        bodyType: ["SUV"],
        specifications: ["GCC"],
        priceMax: 180000,
        yearMin: 2021,
        city: ["Dubai"],
      }),
    );
  });

  it("keeps unsupported condition claims as preferences instead of facts", () => {
    const result = interpretFixturePrompt("Find me a clean accident-free BMW sedan");

    expect(result.intent.conditionPreferences).toContain("Accident history stated");
    expect(result.summary).toContain("preference");
  });

  it("expands compact thousands notation in budgets", () => {
    expect(interpretFixturePrompt("A GCC SUV under AED 180k").intent.priceMax).toBe(180000);
  });
});
