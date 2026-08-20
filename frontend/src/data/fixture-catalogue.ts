import { listingSchema, type Listing } from "@/domain/schemas";
import seedData from "../../../backend/packages/carveo-core/src/carveo_core/data/ae-listings.json";
import { z } from "zod";

type Seed = Pick<Listing, "id" | "make" | "model" | "trim" | "year" | "price" | "mileageKm" | "city" | "bodyType" | "specifications" | "sellerType">;

const seedSchema = z.object({
  id: z.string(), make: z.string(), model: z.string(), trim: z.string(), year: z.number().int(),
  price: z.number().int().nonnegative(), mileageKm: z.number().int().nonnegative(),
  city: listingSchema.shape.city, bodyType: listingSchema.shape.bodyType,
  specifications: listingSchema.shape.specifications, sellerType: listingSchema.shape.sellerType,
});

const seeds: Seed[] = z.array(seedSchema).parse(seedData);

const mediaByBodyType: Record<Listing["bodyType"], string> = {
  SUV: "/media/fixture-suv.jpg",
  Sedan: "/media/fixture-sedan.jpg",
  Coupe: "/media/fixture-coupe.jpg",
  Hatchback: "/media/fixture-hatchback.jpg",
  Pickup: "/media/fixture-pickup.jpg",
  Convertible: "/media/fixture-convertible.jpg",
};

const mediaByModel: Record<string, string> = {
  "Toyota Land Cruiser": "/media/toyota-land-cruiser.jpg",
  "Nissan Patrol": "/media/nissan-patrol.jpg",
  "BMW X5": "/media/bmw-x5.jpg",
  "Mercedes-Benz C 200": "/media/mercedes-c-class.jpg",
};

export const fixtureCatalogue: Listing[] = seeds.map((seed, index) => {
  const unknown = index % 3 === 1;
  const warning = index % 7 === 0;
  const seenDay = String((index % 18) + 1).padStart(2, "0");
  const media = mediaByModel[`${seed.make} ${seed.model}`] ?? mediaByBodyType[seed.bodyType];
  return listingSchema.parse({
    ...seed,
    market: "ae",
    title: `${seed.year} ${seed.make} ${seed.model} ${seed.trim}`,
    currency: "AED",
    source: { name: "Carveo approved fixture", listingUrl: `https://fixtures.carveo.local/listings/${seed.id}`, status: "Fixture" },
    description: `Source-stated fixture record for a ${seed.year} ${seed.make} ${seed.model} in ${seed.city}. Data is illustrative and not a live advertisement.`,
    features: ["Climate control", "Rear camera", index % 2 ? "Cruise control" : "Leather seats", index % 4 ? "Bluetooth" : "Sunroof"],
    photos: [media, media],
    firstSeenAt: `2026-08-${seenDay}T08:00:00.000Z`,
    lastSeenAt: `2026-08-19T${String(8 + (index % 9)).padStart(2, "0")}:00:00.000Z`,
    conditionEvidence: unknown
      ? [{ kind: "unknown", label: "Condition not stated", detail: "The fixture source does not state accident, damage, service, or inspection history." }]
      : warning
        ? [{ kind: "warning", label: "Repair stated", detail: "The source notes a repainted bumper.", sourceClaim: "Rear bumper repainted" }]
        : [{ kind: "positive", label: "Service history stated", detail: "The source states service history is available.", sourceClaim: "Service history available" }],
    priceHistory: [
      { observedAt: "2026-07-20T08:00:00.000Z", price: Math.round(seed.price * 1.04) },
      { observedAt: "2026-08-19T08:00:00.000Z", price: seed.price },
    ],
    duplicateOffers: index % 6 === 0 ? [{ source: "Fixture partner B", price: seed.price + 3000, url: `https://fixtures-b.carveo.local/listings/${seed.id}` }] : [],
  });
});
