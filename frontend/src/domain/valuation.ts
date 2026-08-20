import type { DealPosition } from "@/domain/schemas";

export function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? Math.round((sorted[middle - 1] + sorted[middle]) / 2) : sorted[middle];
}

export function calculateDealPosition(price: number, comparables: number[]): DealPosition {
  if (comparables.length < 4) {
    return { label: "Limited data", typicalPrice: null, differenceAmount: null, differencePercent: null, sampleSize: comparables.length };
  }
  const typicalPrice = median(comparables)!;
  const differenceAmount = price - typicalPrice;
  const differencePercent = Math.round((differenceAmount / typicalPrice) * 100);
  const label = differencePercent <= -8 ? "Below typical" : differencePercent >= 8 ? "Above typical" : "Near typical";
  return { label, typicalPrice, differenceAmount, differencePercent, sampleSize: comparables.length };
}
