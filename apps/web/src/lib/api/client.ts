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
export type NewsItem = Schemas["NewsItemOut"];
export type Timeframe = "1m" | "3m" | "5m" | "15m" | "30m" | "1h" | "4h" | "1d";

// Same sizes and order as the API (backend/app/timeframes.py). The fast sizes get a new
// signal every 1 to 30 minutes; Binance has no 10m candle, so 15m takes its place.
export const FAST_TIMEFRAMES: Timeframe[] = ["1m", "3m", "5m", "15m", "30m"];
export const SLOW_TIMEFRAMES: Timeframe[] = ["1h", "4h", "1d"];
export const TIMEFRAMES: Timeframe[] = [...FAST_TIMEFRAMES, ...SLOW_TIMEFRAMES];
export const DEFAULT_TIMEFRAME: Timeframe = "1h";

export function isTimeframe(value: unknown): value is Timeframe {
  return TIMEFRAMES.includes(value as Timeframe);
}

export function isFast(tf: Timeframe): boolean {
  return FAST_TIMEFRAMES.includes(tf);
}

/** Length of one candle in seconds: "15m" -> 900. */
export function timeframeSeconds(tf: Timeframe): number {
  const unit = { m: 60, h: 3600, d: 86_400 }[tf.slice(-1) as "m" | "h" | "d"];
  return Number(tf.slice(0, -1)) * unit;
}

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
