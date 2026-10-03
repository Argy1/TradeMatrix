"use client";

import { useQuery } from "@tanstack/react-query";

import { ApiError, api, type Timeframe, unwrap } from "./client";

// TanStack Query caches each response and refetches in the background. The worker makes new
// signals once per candle, so polling every 30-60 s is plenty until the WebSocket arrives.

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
    refetchInterval: 30_000,
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
    refetchInterval: 60_000,
  });
}

export function usePerformance(params: { symbol?: string; tf?: Timeframe; days: number }) {
  return useQuery({
    queryKey: ["performance", params.symbol ?? "all", params.tf ?? "all", params.days],
    queryFn: () => unwrap(api.GET("/v1/performance", { params: { query: params } })),
    refetchInterval: 300_000,
  });
}

/** Every coin x timeframe in one request (keeps the track-record page under the rate limit). */
export function usePerformanceSummary(days: number) {
  return useQuery({
    queryKey: ["performance-summary", days],
    queryFn: () => unwrap(api.GET("/v1/performance/summary", { params: { query: { days } } })),
    refetchInterval: 300_000,
  });
}
