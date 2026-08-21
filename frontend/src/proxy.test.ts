import { describe, expect, it, vi } from "vitest";

vi.mock("@clerk/nextjs/server", () => ({
  clerkMiddleware: () => vi.fn(),
}));

import { config } from "@/proxy";

describe("Clerk proxy", () => {
  it("matches Clerk's proxy route after application API routes", () => {
    expect(config.matcher).toContain("/(api|trpc)(.*)");
    expect(config.matcher).toContain("/__clerk/:path*");
    expect(config.matcher.indexOf("/__clerk/:path*")).toBeGreaterThan(
      config.matcher.indexOf("/(api|trpc)(.*)"),
    );
  });
});
