import { afterEach, describe, expect, it, vi } from "vitest";
import { GET } from "@/app/api/ready/route";

describe("GET /api/ready", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("reports ready only when the catalogue API is ready", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response('{"status":"ready"}', { status: 200 })));

    const response = await GET();

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ status: "ready" });
  });

  it("reports unavailable when the catalogue API cannot be reached", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => { throw new Error("offline"); }));

    const response = await GET();

    expect(response.status).toBe(503);
    expect(await response.json()).toEqual({ status: "unavailable" });
  });
});
