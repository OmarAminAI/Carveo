import { listingSchema, type Listing } from "@/domain/schemas";

type Seed = Pick<Listing, "id" | "make" | "model" | "trim" | "year" | "price" | "mileageKm" | "city" | "bodyType" | "specifications" | "sellerType">;

const seeds: Seed[] = [
  { id: "cv-toyota-land-cruiser-2022-01", make: "Toyota", model: "Land Cruiser", trim: "GXR", year: 2022, price: 259000, mileageKm: 61000, city: "Dubai", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-toyota-land-cruiser-2021-02", make: "Toyota", model: "Land Cruiser", trim: "VXR", year: 2021, price: 238000, mileageKm: 79000, city: "Abu Dhabi", bodyType: "SUV", specifications: "GCC", sellerType: "Private" },
  { id: "cv-toyota-land-cruiser-2023-03", make: "Toyota", model: "Land Cruiser", trim: "GXR", year: 2023, price: 289000, mileageKm: 36000, city: "Dubai", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-toyota-land-cruiser-2022-04", make: "Toyota", model: "Land Cruiser", trim: "EXR", year: 2022, price: 247000, mileageKm: 69000, city: "Sharjah", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-toyota-rav4-2022-01", make: "Toyota", model: "RAV4", trim: "Adventure", year: 2022, price: 138000, mileageKm: 43000, city: "Dubai", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-toyota-rav4-2021-02", make: "Toyota", model: "RAV4", trim: "EX", year: 2021, price: 112000, mileageKm: 67000, city: "Abu Dhabi", bodyType: "SUV", specifications: "American", sellerType: "Private" },
  { id: "cv-nissan-patrol-2022-01", make: "Nissan", model: "Patrol", trim: "SE Titanium", year: 2022, price: 219000, mileageKm: 58000, city: "Dubai", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-nissan-patrol-2021-02", make: "Nissan", model: "Patrol", trim: "LE Platinum", year: 2021, price: 229000, mileageKm: 73000, city: "Abu Dhabi", bodyType: "SUV", specifications: "GCC", sellerType: "Private" },
  { id: "cv-nissan-patrol-2023-03", make: "Nissan", model: "Patrol", trim: "SE", year: 2023, price: 245000, mileageKm: 35000, city: "Dubai", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-nissan-patrol-2022-04", make: "Nissan", model: "Patrol", trim: "XE", year: 2022, price: 198000, mileageKm: 84000, city: "Sharjah", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-mercedes-c200-2022-01", make: "Mercedes-Benz", model: "C 200", trim: "AMG Line", year: 2022, price: 184000, mileageKm: 41000, city: "Dubai", bodyType: "Sedan", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-mercedes-c200-2021-02", make: "Mercedes-Benz", model: "C 200", trim: "Avantgarde", year: 2021, price: 149000, mileageKm: 62000, city: "Abu Dhabi", bodyType: "Sedan", specifications: "European", sellerType: "Private" },
  { id: "cv-mercedes-c200-2023-03", make: "Mercedes-Benz", model: "C 200", trim: "AMG Line", year: 2023, price: 209000, mileageKm: 22000, city: "Dubai", bodyType: "Sedan", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-mercedes-c200-2022-04", make: "Mercedes-Benz", model: "C 200", trim: "Premium", year: 2022, price: 171000, mileageKm: 54000, city: "Ajman", bodyType: "Sedan", specifications: "American", sellerType: "Dealer" },
  { id: "cv-bmw-x5-2022-01", make: "BMW", model: "X5", trim: "xDrive40i M Sport", year: 2022, price: 268000, mileageKm: 46000, city: "Dubai", bodyType: "SUV", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-bmw-x5-2021-02", make: "BMW", model: "X5", trim: "xDrive40i", year: 2021, price: 219000, mileageKm: 71000, city: "Abu Dhabi", bodyType: "SUV", specifications: "American", sellerType: "Private" },
  { id: "cv-porsche-911-2021-01", make: "Porsche", model: "911", trim: "Carrera", year: 2021, price: 419000, mileageKm: 33000, city: "Dubai", bodyType: "Coupe", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-porsche-911-2022-02", make: "Porsche", model: "911", trim: "Carrera S", year: 2022, price: 489000, mileageKm: 19000, city: "Abu Dhabi", bodyType: "Coupe", specifications: "European", sellerType: "Dealer" },
  { id: "cv-ford-f150-2021-01", make: "Ford", model: "F-150", trim: "Lariat", year: 2021, price: 169000, mileageKm: 76000, city: "Dubai", bodyType: "Pickup", specifications: "American", sellerType: "Dealer" },
  { id: "cv-ford-f150-2022-02", make: "Ford", model: "F-150", trim: "Raptor", year: 2022, price: 279000, mileageKm: 48000, city: "Sharjah", bodyType: "Pickup", specifications: "GCC", sellerType: "Private" },
  { id: "cv-volkswagen-golf-2022-01", make: "Volkswagen", model: "Golf", trim: "GTI", year: 2022, price: 139000, mileageKm: 39000, city: "Dubai", bodyType: "Hatchback", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-volkswagen-golf-2021-02", make: "Volkswagen", model: "Golf", trim: "R", year: 2021, price: 158000, mileageKm: 56000, city: "Abu Dhabi", bodyType: "Hatchback", specifications: "European", sellerType: "Private" },
  { id: "cv-lexus-lc500-2021-01", make: "Lexus", model: "LC 500", trim: "Convertible", year: 2021, price: 339000, mileageKm: 42000, city: "Dubai", bodyType: "Convertible", specifications: "GCC", sellerType: "Dealer" },
  { id: "cv-lexus-lc500-2022-02", make: "Lexus", model: "LC 500", trim: "Convertible Platinum", year: 2022, price: 379000, mileageKm: 27000, city: "Abu Dhabi", bodyType: "Convertible", specifications: "GCC", sellerType: "Private" },
];

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
