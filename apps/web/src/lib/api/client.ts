import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

// The browser only knows the public API URL. Secrets never reach the web app (CLAUDE.md rule 4).
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// A request stuck on a broken connection would otherwise wait forever (and the page would
// show its loading skeleton forever). After 15 s it fails, and TanStack Query retries it.
const fetchWithTimeout: typeof fetch = (input, init) =>
  fetch(input, { ...init, signal: init?.signal ?? AbortSignal.timeout(15_000) });

/** Typed client generated from the FastAPI OpenAPI schema (`npm run api:types`). */
export const api = createClient<paths>({ baseUrl: API_BASE_URL, fetch: fetchWithTimeout });

type Schemas = components["schemas"];
export type Prediction = Schemas["PredictionOut"];
export type MarketRow = Schemas["MarketRow"];
export type SignalChip = Schemas["SignalChip"];
export type Candle = Schemas["CandleOut"];
export type HistoryItem = Schemas["HistoryItem"];
export type Performance = Schemas["PerformanceOut"];
export type Timeframe = "1h" | "4h" | "1d";

export const TIMEFRAMES: Timeframe[] = ["1h", "4h", "1d"];

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

/** Turn an openapi-fetch result into data, or throw the API's {"error": {...}} as ApiError. */
export async function unwrap<T>(
  call: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await call;
  if (error !== undefined || data === undefined) {
    const body = error as { error?: { code?: string; message?: string } } | undefined;
    throw new ApiError(
      response.status,
      body?.error?.code ?? "error",
      body?.error?.message ?? `Request failed (${response.status})`,
    );
  }
  return data;
}
