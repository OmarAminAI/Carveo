export type Intent = {
  market?: string;
  city?: string;
  make?: string;
  models: string[];
  body_types: string[];
  year_min?: number;
  year_max?: number;
  budget_max?: number;
  currency?: string;
  mileage_max_km?: number;
  colors: string[];
  specifications: string[];
  condition_preferences: string[];
};

export type IntentState = {
  intent: Intent;
  ready: boolean;
  missing_fields: string[];
  next_question?: string;
};

export type SearchSession = { session_id: string; intent_state: IntentState };

export type Match = {
  score: number;
  reasons: string[];
  warnings: string[];
  listing: {
    id: string;
    source_name: string;
    source_url: string;
    title: string;
    price: number;
    currency: string;
    city: string;
    year: number;
    mileage_km: number;
    color?: string;
    specifications: string[];
    seller_type: string;
    warranty: boolean;
    condition_signals: string[];
  };
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers: { "Content-Type": "application/json", ...options?.headers } });
  if (!response.ok) throw new Error("Carveo could not complete that request.");
  return response.json() as Promise<T>;
}

export const createSession = () => request<SearchSession>("/sessions", { method: "POST" });
export const sendMessage = (sessionId: string, content: string) => request<{ message: { role: "assistant"; content: string }; intent_state: IntentState }>(`/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ content }) });
export const getResults = (sessionId: string) => request<{ intent: Intent; matches: Match[] }>(`/sessions/${sessionId}/results`);

