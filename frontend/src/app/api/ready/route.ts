const apiUrl = process.env.CARVEO_API_INTERNAL_URL ?? "http://localhost:8000";

export async function GET(): Promise<Response> {
  try {
    const response = await fetch(`${apiUrl}/ready`, {
      cache: "no-store",
      signal: AbortSignal.timeout(2_000),
    });
    if (!response.ok) {
      return Response.json({ status: "unavailable" }, { status: 503 });
    }
    return Response.json({ status: "ready" });
  } catch {
    return Response.json({ status: "unavailable" }, { status: 503 });
  }
}
