"use client";

import { useSyncExternalStore } from "react";

import { DEFAULT_TIMEFRAME, isTimeframe, type Timeframe } from "./api/client";

// The candle size picked on the markets list, the watchlist and the track record. It is
// remembered on this device only (it is a display choice, not account data).
const KEY = "tm-size";
const EVENT = "tm-size-change";
// Fallback when browser storage is blocked (private mode): remember for this page visit only.
let memory: Timeframe | null = null;

function read(): Timeframe {
  if (memory) return memory;
  try {
    const stored = localStorage.getItem(KEY);
    return isTimeframe(stored) ? stored : DEFAULT_TIMEFRAME;
  } catch {
    return DEFAULT_TIMEFRAME;
  }
}

function subscribe(onChange: () => void) {
  window.addEventListener(EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

/** [picked size, pick another]. The server renders the default; the browser then shows the stored one. */
export function usePickedSize(): [Timeframe, (tf: Timeframe) => void] {
  const size = useSyncExternalStore(subscribe, read, () => DEFAULT_TIMEFRAME);
  const pick = (tf: Timeframe) => {
    memory = tf;
    try {
      localStorage.setItem(KEY, tf);
    } catch {}
    window.dispatchEvent(new Event(EVENT));
  };
  return [size, pick];
}
