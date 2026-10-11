"use client";

import { useQuery } from "@tanstack/react-query";

import { ApiError, api, isFast, type Timeframe, unwrap } from "./client";

// TanStack Query caches each response and refetches in the background. The worker makes new
// signals once per candle. New signals arrive over the WebSocket (lib/api/live.ts); polling is
// the safety net if a message is missed, so the fast candle sizes poll more often.

export function useMarkets() {
  return useQuery({
    queryKey: ["markets"],
    queryFn: () => unwrap(api.GET("/v1/markets")),
    refetchInterval: 60_000,
  });
}

export function useLatestPrediction(symbol: string, tf: Timeframe) {
  return useQuery({
    queryKey: ["prediction", symbol, tf],
    queryFn: () => unwrap(api.GET("/v1/predictions/latest", { params: { query: { symbol, tf } } })),
    refetchInterval: isFast(tf) ? 10_000 : 30_000,
    retry: (count, error) => !(error instanceof ApiError && error.status === 404) && count < 2,
  });
}

export function useCandles(symbol: string, tf: Timeframe, limit = 300) {
  return useQuery({
    queryKey: ["candles", symbol, tf, limit],
    queryFn: () => unwrap(api.GET("/v1/candles", { params: { query: { symbol, tf, limit } } })),
    refetchInterval: 60_000,
  });
}

export function useHistory(symbol: string, tf: Timeframe, limit = 12) {
  return useQuery({
    queryKey: ["history", symbol, tf, limit],
    queryFn: () =>
      unwrap(api.GET("/v1/predictions/history", { params: { query: { symbol, tf, limit } } })),
    refetchInterval: isFast(tf) ? 20_000 : 60_000,
  });
}

export function usePerformance(params: { symbol?: string; tf?: Timeframe; days: number }) {
  return useQuery({
    queryKey: ["performance", params.symbol ?? "all", params.tf ?? "all", params.days],
    queryFn: () => unwrap(api.GET("/v1/performance", { params: { query: params } })),
    refetchInterval: 300_000,
  });
}

/** Recent headlines about one coin. The worker looks for news every 15 minutes. */
export function useNews(symbol: string, limit = 8) {
  return useQuery({
    queryKey: ["news", symbol, limit],
    queryFn: () => unwrap(api.GET("/v1/news", { params: { query: { symbol, limit } } })),
    refetchInterval: 300_000,
  });
}

/** Every coin of one candle size in one request (keeps the track-record page under the rate limit). */
export function usePerformanceSummary(days: number, tf: Timeframe) {
  return useQuery({
    queryKey: ["performance-summary", days, tf],
    queryFn: () => unwrap(api.GET("/v1/performance/summary", { params: { query: { days, tf } } })),
    refetchInterval: 300_000,
  });
}
