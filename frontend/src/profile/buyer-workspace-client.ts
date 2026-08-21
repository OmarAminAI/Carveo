import { z } from "zod";
import type { components } from "@/contracts/api";
import {
  buyerWorkspaceSchema,
  conversationSchema,
  conversationSummarySchema,
  savedSearchSchema,
  workspaceMergeResponseSchema,
  type BrowserProfile,
  type BuyerWorkspace,
  type Conversation,
  type ConversationSummary,
  type SavedSearch,
  type WorkspaceMergeResponse,
} from "@/domain/schemas";

type AnonymousMergeRequest = components["schemas"]["AnonymousWorkspaceMergeRequest"];
type ComparisonUpdate = components["schemas"]["ComparisonUpdate"];
type ConversationCreate = components["schemas"]["ConversationCreate"];
type ConversationTurnCreate = components["schemas"]["ConversationTurnCreate"];
type SavedSearchUpsert = components["schemas"]["SavedSearchUpsert"];
type TokenOptions = { skipCache?: boolean };
type GetToken = (options?: TokenOptions) => Promise<string | null>;

export class WorkspaceRequestError extends Error {
  constructor(public readonly status: number, message = `Buyer workspace request failed (${status})`) {
    super(message);
    this.name = "WorkspaceRequestError";
  }
}

export class BuyerWorkspaceClient {
  private readonly baseUrl: string;

  constructor(
    baseUrl: string,
    private readonly getToken: GetToken,
    private readonly fetcher: typeof fetch = fetch,
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  private async request<T>(path: string, schema: z.ZodType<T>, init: RequestInit = {}): Promise<T> {
    const execute = async (options?: TokenOptions) => {
      const token = options ? await this.getToken(options) : await this.getToken();
      if (!token) throw new WorkspaceRequestError(401, "A signed-in buyer session is required");
      const headers = new Headers(init.headers);
      headers.set("Authorization", `Bearer ${token}`);
      if (init.body !== undefined) headers.set("Content-Type", "application/json");
      return this.fetcher(`${this.baseUrl}${path}`, { ...init, headers });
    };

    let response = await execute();
    if (response.status === 401) response = await execute({ skipCache: true });
    if (!response.ok) throw new WorkspaceRequestError(response.status);
    return schema.parse(await response.json());
  }

  private async requestEmpty(path: string, init: RequestInit): Promise<void> {
    const execute = async (options?: TokenOptions) => {
      const token = options ? await this.getToken(options) : await this.getToken();
      if (!token) throw new WorkspaceRequestError(401, "A signed-in buyer session is required");
      const headers = new Headers(init.headers);
      headers.set("Authorization", `Bearer ${token}`);
      return this.fetcher(`${this.baseUrl}${path}`, { ...init, headers });
    };
    let response = await execute();
    if (response.status === 401) response = await execute({ skipCache: true });
    if (!response.ok) throw new WorkspaceRequestError(response.status);
  }

  getWorkspace(): Promise<BuyerWorkspace> {
    return this.request("/api/v1/me/workspace", buyerWorkspaceSchema);
  }

  mergeAnonymous(payload: AnonymousMergeRequest): Promise<WorkspaceMergeResponse> {
    return this.request("/api/v1/me/workspace/merge", workspaceMergeResponseSchema, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  addShortlist(listingId: string): Promise<BuyerWorkspace> {
    return this.request(`/api/v1/me/shortlist/${encodeURIComponent(listingId)}`, buyerWorkspaceSchema, {
      method: "PUT",
    });
  }

  removeShortlist(listingId: string): Promise<BuyerWorkspace> {
    return this.request(`/api/v1/me/shortlist/${encodeURIComponent(listingId)}`, buyerWorkspaceSchema, {
      method: "DELETE",
    });
  }

  replaceComparison(listingIds: ComparisonUpdate["listingIds"]): Promise<BuyerWorkspace> {
    return this.request("/api/v1/me/comparison", buyerWorkspaceSchema, {
      method: "PUT",
      body: JSON.stringify({ listingIds }),
    });
  }

  listSavedSearches(): Promise<SavedSearch[]> {
    return this.request("/api/v1/me/saved-searches", z.array(savedSearchSchema));
  }

  upsertSavedSearch(payload: SavedSearchUpsert): Promise<SavedSearch> {
    return this.request("/api/v1/me/saved-searches", savedSearchSchema, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  deleteSavedSearch(savedSearchId: string): Promise<void> {
    return this.requestEmpty(`/api/v1/me/saved-searches/${encodeURIComponent(savedSearchId)}`, { method: "DELETE" });
  }

  listConversations(): Promise<ConversationSummary[]> {
    return this.request("/api/v1/me/conversations", z.array(conversationSummarySchema));
  }

  createConversation(payload: ConversationCreate): Promise<Conversation> {
    return this.request("/api/v1/me/conversations", conversationSchema, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  getConversation(conversationId: string): Promise<Conversation> {
    return this.request(`/api/v1/me/conversations/${encodeURIComponent(conversationId)}`, conversationSchema);
  }

  appendTurn(conversationId: string, payload: ConversationTurnCreate): Promise<Conversation> {
    return this.request(`/api/v1/me/conversations/${encodeURIComponent(conversationId)}/turns`, conversationSchema, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
}

export function toAnonymousMergePayload(profile: BrowserProfile): AnonymousMergeRequest {
  return {
    shortlistListingIds: profile.shortlistIds,
    comparisonListingIds: profile.compareIds,
    savedSearches: profile.savedSearchDrafts.map(({ label, query }) => ({ label, query })),
    conversations: profile.anonymousConversations.map((conversation) => ({
      clientId: conversation.clientId,
      title: conversation.title,
      interpretedIntent: conversation.interpretedIntent,
      turns: conversation.turns.map(({ role, content }) => ({ role, content })),
    })),
  };
}

export function applyWorkspace(profile: BrowserProfile, workspace: BuyerWorkspace): BrowserProfile {
  return {
    ...profile,
    shortlistIds: workspace.shortlistListingIds,
    compareIds: workspace.comparisonListingIds,
    savedSearchDrafts: workspace.savedSearches.map((search) => ({
      id: search.id,
      label: search.label,
      query: search.query,
      savedAt: search.updatedAt,
    })),
    anonymousConversations: [],
  };
}
