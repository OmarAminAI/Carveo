export type ConditionEvidence = { claim: string; evidence?: string; confidence: number };
export type Listing = { id: string; market: string; source_id: string; source_name: string; source_url: string; source_status: string; title: string; make: string; model: string; trim?: string; body_type: string; price: number; currency: string; typical_price?: number; deal_label: "Great deal" | "Good deal" | "Fair price" | "Verify price"; deal_difference?: number; year: number; mileage_km: number; city: string; seller_type: string; regional_specs?: string; color?: string; warranty: boolean; condition: ConditionEvidence[]; features: string[]; photos: string[]; first_seen_at: string; last_seen_at: string; freshness_hours: number };
export type ListingPage = { items: Listing[]; total: number; page: number; page_size: number; available_filters: Record<string, string[]> };
export type SavedSearch = { id: string; profile_id: string; name: string; query: Record<string, string | number | boolean | null>; priority_refresh: boolean };
export type Intent = { market?: string; city?: string; make?: string; models: string[]; body_types: string[]; year_min?: number; year_max?: number; budget_max?: number; currency?: string; mileage_max_km?: number; colors: string[]; specifications: string[]; condition_preferences: string[] };
export type IntentState = { intent: Intent; ready: boolean; missing_fields: string[]; next_question?: string };

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
async function request<T>(path: string, options?: RequestInit): Promise<T> { const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers: { "Content-Type": "application/json", ...options?.headers } }); if (!response.ok) throw new Error("Carveo could not complete that request."); return response.json() as Promise<T>; }
export const getListings = (params: URLSearchParams) => request<ListingPage>(`/listings?${params.toString()}`);
export const getListing = (id: string) => request<Listing>(`/listings/${id}`);
export const compareListings = (listing_ids: string[]) => request<{ listings: Listing[] }>("/compare", { method: "POST", body: JSON.stringify({ listing_ids }) });
export const getSavedSearches = (profileId: string) => request<SavedSearch[]>(`/profile/searches?profile_id=${encodeURIComponent(profileId)}`);
export const saveSearch = (data: Omit<SavedSearch, "id">) => request<SavedSearch>("/profile/searches", { method: "PUT", body: JSON.stringify(data) });
export const deleteSavedSearch = (id: string, profileId: string) => request<void>(`/profile/searches/${id}?profile_id=${encodeURIComponent(profileId)}`, { method: "DELETE" });
export const createSession = () => request<{ session_id: string; intent_state: IntentState }>("/sessions", { method: "POST" });
export const sendMessage = (sessionId: string, content: string) => request<{ message: { role: "assistant"; content: string }; intent_state: IntentState }>(`/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ content }) });
