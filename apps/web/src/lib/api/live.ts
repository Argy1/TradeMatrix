"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import type { Candle, Prediction, Timeframe } from "./client";

export const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

type CandleMessage = {
  type: "candle";
  symbol: string;
  tf: Timeframe;
  candle: { t: string; o: string; h: string; l: string; c: string; v: string; closed: boolean };
};
type PredictionMessage = { type: "prediction"; symbol: string; tf: Timeframe; prediction: Prediction };
type StreamMessage = CandleMessage | PredictionMessage | { type: "ping" };

export type LiveStatus = "connecting" | "live" | "offline";

const EMPTY_INDICATORS = {
  ema9: null, ema21: null, ema50: null, bb_upper: null, bb_mid: null, bb_lower: null,
  rsi14: null, macd: null, macd_signal: null, macd_hist: null,
} as const; // prettier-ignore

/** Merge a live candle into the cached list: replace the forming bar or append a new one. */
export function mergeCandle(candles: Candle[], live: CandleMessage["candle"]): Candle[] {
  const last = candles.at(-1);
  const bar: Candle = { ...EMPTY_INDICATORS, ...last, t: live.t, o: live.o, h: live.h, l: live.l, c: live.c, v: live.v };
  if (last && last.t === live.t) return [...candles.slice(0, -1), bar];
  if (last && Date.parse(live.t) < Date.parse(last.t)) return candles; // late message: ignore
  // A new bar: indicators are only computed for closed candles, so they stay empty here.
  return [...candles, { ...bar, ...EMPTY_INDICATORS }];
}

/**
 * Live updates for one coin and candle size over /ws/stream (docs/04).
 * The page keeps working without it: queries still refetch on their own timers.
 */
export function useLiveStream(symbol: string, tf: Timeframe, candleLimit: number) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<LiveStatus>("connecting");
  const [updating, setUpdating] = useState(false);
  const updatingTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | null = null;
    let attempt = 0;
    let stopped = false;
    const candlesKey = ["candles", symbol, tf, candleLimit];
    const predictionKey = ["prediction", symbol, tf];

    const stopUpdating = () => {
      setUpdating(false);
      if (updatingTimer.current) clearTimeout(updatingTimer.current);
    };

    const connect = () => {
      setStatus("connecting");
      socket = new WebSocket(`${WS_URL}/ws/stream?symbols=${symbol}&tf=${tf}`);
      socket.onopen = () => {
        if (attempt > 0) {
          // After a reconnect, re-fetch what may have changed while we were away.
          queryClient.invalidateQueries({ queryKey: candlesKey });
          queryClient.invalidateQueries({ queryKey: predictionKey });
        }
        attempt = 0;
        setStatus("live");
      };
      socket.onmessage = (event) => {
        const message = JSON.parse(event.data) as StreamMessage;
        if (message.type === "ping") {
          socket?.send(JSON.stringify({ type: "pong" }));
          return;
        }
        if (message.symbol !== symbol || message.tf !== tf) return;
        if (message.type === "candle") {
          queryClient.setQueryData(candlesKey, (old: { candles: Candle[] } | undefined) =>
            old ? { ...old, candles: mergeCandle(old.candles, message.candle) } : old,
          );
          if (message.candle.closed) {
            // The worker stores the closed candle and predicts within ~30 s (docs/08 state).
            setUpdating(true);
            if (updatingTimer.current) clearTimeout(updatingTimer.current);
            updatingTimer.current = setTimeout(stopUpdating, 30_000);
            setTimeout(() => queryClient.invalidateQueries({ queryKey: candlesKey }), 10_000);
          }
        } else if (message.type === "prediction") {
          queryClient.setQueryData(predictionKey, message.prediction);
          queryClient.invalidateQueries({ queryKey: ["history", symbol, tf] });
          queryClient.invalidateQueries({ queryKey: ["markets"] });
          stopUpdating();
        }
      };
      socket.onclose = () => {
        if (stopped) return;
        setStatus("offline");
        attempt += 1;
        retry = setTimeout(connect, Math.min(1000 * 2 ** attempt, 30_000));
      };
    };

    connect();
    return () => {
      stopped = true;
      if (retry) clearTimeout(retry);
      if (updatingTimer.current) clearTimeout(updatingTimer.current);
      socket?.close();
    };
  }, [symbol, tf, candleLimit, queryClient]);

  return { status, updating };
}
