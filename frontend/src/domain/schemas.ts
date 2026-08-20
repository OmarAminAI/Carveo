import { z } from "zod";

export const conditionEvidenceSchema = z.object({
  kind: z.enum(["positive", "warning", "unknown"]),
  label: z.string(),
  detail: z.string(),
  sourceClaim: z.string().nullable().optional(),
});

export const priceObservationSchema = z.object({
  observedAt: z.string(),
  price: z.number().nonnegative(),
});

export const dealPositionSchema = z.object({
  label: z.enum(["Below typical", "Near typical", "Above typical", "Limited data"]),
  typicalPrice: z.number().nullable(),
  differenceAmount: z.number().nullable(),
  differencePercent: z.number().nullable(),
  sampleSize: z.number().int().nonnegative(),
});

export const listingSchema = z.object({
  id: z.string(),
  market: z.literal("ae"),
  title: z.string(),
  make: z.string(),
  model: z.string(),
  trim: z.string(),
  year: z.number().int(),
  price: z.number().nonnegative(),
  currency: z.literal("AED"),
  mileageKm: z.number().nonnegative(),
  city: z.enum(["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]),
  bodyType: z.enum(["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"]),
  specifications: z.enum(["GCC", "American", "European", "Japanese"]),
  sellerType: z.enum(["Dealer", "Private"]),
  source: z.object({
    name: z.string(),
    listingUrl: z.string().url(),
    status: z.enum(["Fixture", "Approved"]),
  }),
  description: z.string(),
  features: z.array(z.string()),
  photos: z.array(z.string()).min(1),
  firstSeenAt: z.string(),
  lastSeenAt: z.string(),
  conditionEvidence: z.array(conditionEvidenceSchema),
  priceHistory: z.array(priceObservationSchema),
  duplicateOffers: z.array(z.object({ source: z.string(), price: z.number(), url: z.string().url() })),
  dealPosition: dealPositionSchema.nullable().optional(),
});

export type Listing = z.infer<typeof listingSchema>;
export type ConditionEvidence = z.infer<typeof conditionEvidenceSchema>;
export type PriceObservation = z.infer<typeof priceObservationSchema>;
export type DealPosition = z.infer<typeof dealPositionSchema>;

export const listingSortSchema = z.enum(["best-match", "best-deal", "newest", "lowest-price", "lowest-mileage"]);
export type ListingSort = z.infer<typeof listingSortSchema>;

export type ListingQuery = {
  market: "ae";
  q: string;
  make: string[];
  model: string[];
  bodyType: string[];
  yearMin?: number;
  yearMax?: number;
  priceMin?: number;
  priceMax?: number;
  mileageMax?: number;
  specifications: string[];
  sellerType: string[];
  evidence: string[];
  city: string[];
  sort: ListingSort;
  page: number;
  pageSize: number;
};

export type ListingPage = {
  items: Listing[];
  total: number;
  page: number;
  pageSize: number;
  pageCount: number;
};

export type SearchIntent = Partial<Omit<ListingQuery, "market" | "sort" | "page" | "pageSize">> & {
  conditionPreferences?: string[];
};

export type AssistantTurn = {
  id: string;
  role: "buyer" | "assistant";
  content: string;
};

export type ModelMarketSummary = {
  make: string;
  model: string;
  activeListings: number;
  medianPrice: number;
  minPrice: number;
  maxPrice: number;
  minMileage: number;
  maxMileage: number;
  lastUpdatedAt: string;
};

export type ComparisonSelection = { listingIds: string[]; max: 4 };

export type BrowserProfile = {
  version: 1;
  id: string;
  shortlistIds: string[];
  compareIds: string[];
  recentViewIds: string[];
  savedSearchDrafts: Array<{ id: string; label: string; query: string; savedAt: string }>;
  assistantDraft: string;
};
