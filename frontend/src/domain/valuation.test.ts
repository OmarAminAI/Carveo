import { describe, expect, it } from "vitest";
import { calculateDealPosition, median } from "@/domain/valuation";

describe("valuation", () => {
  it("uses a robust median for odd and even comparable sets", () => {
    expect(median([120000, 90000, 110000])).toBe(110000);
    expect(median([100000, 160000, 120000, 140000])).toBe(130000);
  });

  it("labels a material discount while exposing the comparison basis", () => {
    const position = calculateDealPosition(105000, [130000, 125000, 135000, 128000, 132000]);

    expect(position).toEqual({
      label: "Below typical",
      typicalPrice: 130000,
      differenceAmount: -25000,
      differencePercent: -19,
      sampleSize: 5,
    });
  });

  it("declines to label sparse segments", () => {
    expect(calculateDealPosition(105000, [100000, 110000])).toEqual({
      label: "Limited data",
      typicalPrice: null,
      differenceAmount: null,
      differencePercent: null,
      sampleSize: 2,
    });
  });
});
