import { listingSortSchema, type ListingQuery } from "@/domain/schemas";

const arrayKeys = ["make", "model", "bodyType", "specifications", "sellerType", "evidence", "city"] as const;
const numberKeys = ["yearMin", "yearMax", "priceMin", "priceMax", "mileageMax"] as const;

const positiveNumber = (value: string | null) => {
  if (!value) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined;
};

export function parseListingQuery(params: URLSearchParams): ListingQuery {
  const sortResult = listingSortSchema.safeParse(params.get("sort"));
  const page = Math.max(1, Math.floor(positiveNumber(params.get("page")) ?? 1));
  const requestedPageSize = Math.floor(positiveNumber(params.get("pageSize")) ?? 12);
  const query: ListingQuery = {
    market: "ae",
    q: params.get("q")?.trim() ?? "",
    make: [],
    model: [],
    bodyType: [],
    specifications: [],
    sellerType: [],
    evidence: [],
    city: [],
    sort: sortResult.success ? sortResult.data : "best-match",
    page,
    pageSize: [12, 24, 48].includes(requestedPageSize) ? requestedPageSize : 24,
  };

  for (const key of arrayKeys) query[key] = [...new Set(params.getAll(key).map((value) => value.trim()).filter(Boolean))];
  for (const key of numberKeys) query[key] = positiveNumber(params.get(key));
  return query;
}

export function toListingSearchParams(query: ListingQuery): URLSearchParams {
  const params = new URLSearchParams();
  if (query.q) params.set("q", query.q);
  for (const key of arrayKeys) for (const value of query[key]) params.append(key, value);
  for (const key of numberKeys) if (query[key] !== undefined) params.set(key, String(query[key]));
  if (query.sort !== "best-match") params.set("sort", query.sort);
  if (query.page !== 1) params.set("page", String(query.page));
  if (query.pageSize !== 12) params.set("pageSize", String(query.pageSize));
  return params;
}

export function slugifyVehicleName(value: string) {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}
